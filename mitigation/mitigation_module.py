from ryu.controller import ofp_event
from ryu.controller.handler import MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib import hub
import Codes.Mitigation.switchm as switchm
from datetime import datetime
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix

class SimpleMonitor13(switchm.SimpleSwitch13):

    def __init__(self, *args, **kwargs):
        super(SimpleMonitor13, self).__init__(*args, **kwargs)
        self.datapaths = {}
        self.monitor_thread = hub.spawn(self._monitor)
        self.flow_training()

    @set_ev_cls(ofp_event.EventOFPStateChange,
                [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            if datapath.id not in self.datapaths:
                self.logger.debug('register datapath: %016x', datapath.id)
                self.datapaths[datapath.id] = datapath
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                self.logger.debug('unregister datapath: %016x', datapath.id)
                del self.datapaths[datapath.id]

    def _monitor(self):
        while True:
            for dp in self.datapaths.values():
                self._request_stats(dp)
            hub.sleep(10)
            self.flow_predict()

    def _request_stats(self, datapath):
        self.logger.debug('send stats request: %016x', datapath.id)
        parser = datapath.ofproto_parser
        req = parser.OFPFlowStatsRequest(datapath)
        datapath.send_msg(req)

    @set_ev_cls(ofp_event.EventOFPFlowStatsReply, MAIN_DISPATCHER)
    def _flow_stats_reply_handler(self, ev):
        timestamp = datetime.now().timestamp()
        with open("PredictFlowStatsfile.csv", "w") as file0:
            file0.write('timestamp,datapath_id,flow_id,ip_src,tp_src,ip_dst,tp_dst,ip_proto,icmp_code,icmp_type,flow_duration_sec,flow_duration_nsec,idle_timeout,hard_timeout,flags,packet_count,byte_count,packet_count_per_second,packet_count_per_nsecond,byte_count_per_second,byte_count_per_nsecond\n')
            body = ev.msg.body
            icmp_code, icmp_type, tp_src, tp_dst = -1, -1, 0, 0
            for stat in sorted([flow for flow in body if flow.priority == 1], key=lambda flow: (flow.match['eth_type'], flow.match['ipv4_src'], flow.match['ipv4_dst'], flow.match['ip_proto'])):
                ip_src, ip_dst, ip_proto = stat.match['ipv4_src'], stat.match['ipv4_dst'], stat.match['ip_proto']
                if ip_proto == 1:
                    icmp_code, icmp_type = stat.match.get('icmpv4_code', -1), stat.match.get('icmpv4_type', -1)
                elif ip_proto == 6:
                    tp_src, tp_dst = stat.match.get('tcp_src', 0), stat.match.get('tcp_dst', 0)
                elif ip_proto == 17:
                    tp_src, tp_dst = stat.match.get('udp_src', 0), stat.match.get('udp_dst', 0)
                flow_id = str(ip_src) + str(tp_src) + str(ip_dst) + str(tp_dst) + str(ip_proto)
                try:
                    packet_count_per_second = stat.packet_count / stat.duration_sec
                    packet_count_per_nsecond = stat.packet_count / stat.duration_nsec
                except:
                    packet_count_per_second, packet_count_per_nsecond = 0, 0
                try:
                    byte_count_per_second = stat.byte_count / stat.duration_sec
                    byte_count_per_nsecond = stat.byte_count / stat.duration_nsec
                except:
                    byte_count_per_second, byte_count_per_nsecond = 0, 0
                file0.write("{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{},{}\n".format(timestamp, ev.msg.datapath.id, flow_id, ip_src, tp_src, ip_dst, tp_dst, ip_proto, icmp_code, icmp_type, stat.duration_sec, stat.duration_nsec, stat.idle_timeout, stat.hard_timeout, stat.flags, stat.packet_count, stat.byte_count, packet_count_per_second, packet_count_per_nsecond, byte_count_per_second, byte_count_per_nsecond))

    def flow_training(self):
        self.logger.info("Flow Training ...")
        flow_dataset = pd.read_csv('FlowStatsfile.csv')
        flow_dataset.iloc[:, 2:6] = flow_dataset.iloc[:, 2:6].replace('.', '', regex=True)
        X_flow = flow_dataset.iloc[:, :-1].astype('float64').values
        y_flow = flow_dataset.iloc[:, -1].values
        X_flow_train, X_flow_test, y_flow_train, y_flow_test = train_test_split(X_flow, y_flow, test_size=0.25, random_state=0)
        classifier = RandomForestClassifier(n_estimators=10, criterion="entropy", random_state=0)
        self.flow_model = classifier.fit(X_flow_train, y_flow_train)
        y_flow_pred = self.flow_model.predict(X_flow_test)
        self.logger.info("------------------------------------------------------------------------------")
        self.logger.info("Confusion Matrix")
        self.logger.info(confusion_matrix(y_flow_test, y_flow_pred))

    def flow_predict(self):
        try:
            predict_flow_dataset = pd.read_csv('PredictFlowStatsfile.csv')
            predict_flow_dataset.iloc[:, 2:6] = predict_flow_dataset.iloc[:, 2:6].replace('.', '', regex=True)
            X_predict_flow = predict_flow_dataset.values.astype('float64')
            y_flow_pred = self.flow_model.predict(X_predict_flow)
            legitimate_trafic = sum(y_flow_pred == 0)
            ddos_trafic = sum(y_flow_pred != 0)
            if (legitimate_trafic / len(y_flow_pred) * 100) > 80:
                self.logger.info("Traffic is Legitimate!")
            else:
                self.logger.info("NOTICE!! DoS Attack in Progress!!!")
                victim = int(predict_flow_dataset['tp_dst'].iloc[y_flow_pred != 0].iloc[0]) % 20
                self.logger.info("Victim Host: h{}".format(victim))
                print("Mitigation process in progress!")
                self.mitigation = 1
            self.logger.info("------------------------------------------------------------------------------")
            with open("PredictFlowStatsfile.csv", "w") as file0:
                file0.write('timestamp,datapath_id,flow_id,ip_src,tp_src,ip_dst,tp_dst,ip_proto,icmp_code,icmp_type,flow_duration_sec,flow_duration_nsec,idle_timeout,hard_timeout,flags,packet_count,byte_count,packet_count_per_second,packet_count_per_nsecond,byte_count_per_second,byte_count_per_nsecond\n')
        except:
            pass
