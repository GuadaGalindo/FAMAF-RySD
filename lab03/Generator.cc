#ifndef GENERATOR
#define GENERATOR

#include <string.h>
#include <omnetpp.h>

using namespace omnetpp;

class Generator : public cSimpleModule {
private:
    cMessage *sendMsgEvent;
    cStdDev transmissionStats;
    cStdDev packetsSent;
public:
    Generator();
    virtual ~Generator();
protected:
    virtual void initialize();
    virtual void finish();
    virtual void handleMessage(cMessage *msg);
};
Define_Module(Generator);

Generator::Generator() {
    sendMsgEvent = NULL;

}

Generator::~Generator() {
    cancelAndDelete(sendMsgEvent);
}

void Generator::initialize() {
    transmissionStats.setName("TotalTransmissions");
    packetsSent.setName("PacketsSent");
    // create the send packet
    sendMsgEvent = new cMessage("sendEvent");
    // schedule the first event at random time
    scheduleAt(par("generationInterval"), sendMsgEvent);
    // packetsSent = 0;
}

void Generator::finish() {
    recordScalar("Number of packets sent", packetsSent.getCount());
}

void Generator::handleMessage(cMessage *msg) {

    // create new packet
    cPacket *pkt;
    pkt = new cPacket("packet");
    pkt->setByteLength(par("packetByteSize"));
    pkt->setKind(1);
    packetsSent.collect(1);

    // cMessage *pkt = new cMessage("packet");
    // send to the output
    send(pkt, "out");

    // compute the new departure time
    simtime_t departureTime = simTime() + par("generationInterval");
    // schedule the new packet generation
    scheduleAt(departureTime, sendMsgEvent);
}

#endif /* GENERATOR */
