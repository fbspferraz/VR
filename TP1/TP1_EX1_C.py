from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import ether_types
from asyncio.log import logger


class SimpleSwitch13(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SimpleSwitch13, self).__init__(*args, **kwargs)
        self.switching_table = {}
        
    def add_entry_to_table(self,port,addr):
    	self.switching_table[int(port)] = addr
    	
    def acess_switching_table(self,addr):
    	for switch_port in self.switching_table:
    		if addr == self.switching_table[switch_port]:
    			return True
    	return False
    	
    def get_switch_port(self,addr):
    	for switch_port in self.switching_table:
    		if addr == self.switching_table[switch_port]:
    			return switch_port
    			
    def print_switching_table(self):
    	logger.info("##################")
    	logger.info("Switching Table")
    	logger.info("PORT \t ADDR")
    	for port, addr in self.switching_table.items():
        	logger.info("%s \t %s", port, addr)
    	logger.info("##################")

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        match = parser.OFPMatch()
        actions = [parser.OFPActionOutput(ofproto.OFPP_CONTROLLER,
                                          ofproto.OFPCML_NO_BUFFER)]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions, buffer_id=None):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS,
                                             actions)]
        if buffer_id:
            mod = parser.OFPFlowMod(datapath=datapath, buffer_id=buffer_id,
                                    priority=priority, match=match,
                                    instructions=inst)
        else:
            mod = parser.OFPFlowMod(datapath=datapath, priority=priority,
                                    match=match, instructions=inst)
        datapath.send_msg(mod)

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser
        in_port = msg.match['in_port']

        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocols(ethernet.ethernet)[0]

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # ignore lldp packet
            return
       
        self.add_entry_to_table(in_port, eth.src)
        self.print_switching_table()

        if self.acess_switching_table(eth.dst):
            self.logger.info("Destination address found in Switching table, packet will be forward to respective destination port")
            out_port = self.get_switch_port(eth.dst)
        else: 
            self.logger.info("Destination address (%s) not found, packet will be flooded", eth.dst)
            out_port = ofproto.OFPP_FLOOD
       
       
       
        actions = [parser.OFPActionOutput(out_port)]
       
        data = None
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = parser.OFPPacketOut(datapath=datapath, buffer_id=msg.buffer_id,
                                  in_port=in_port, actions=actions, data=data)
        datapath.send_msg(out)