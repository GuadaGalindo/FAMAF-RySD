#ifndef TRANSPORTRX
#define TRANSPORTRX

#include <string.h>
#include <omnetpp.h>
#include "packet_m.h"

using namespace omnetpp;

class TransportRx : public cSimpleModule {
    private:
        cQueue buffer;
        cMessage *endServiceEvent;
        simtime_t serviceTime;
        cOutVector bufferSizeVector;
        cOutVector packetDropVector;
        int droppedCounter;
    public:
        TransportRx();
        virtual ~TransportRx();
    protected:
        virtual void initialize();
        virtual void finish();
        virtual void handleMessage(cMessage *msg);
};

Define_Module(TransportRx);

TransportRx::TransportRx() {
    endServiceEvent = NULL;
}

TransportRx::~TransportRx() {
    cancelAndDelete(endServiceEvent);
}

void TransportRx::initialize() {
    buffer.setName("buffer");
    endServiceEvent = new cMessage("endService");
    bufferSizeVector.setName("bufferSizeVector");
    packetDropVector.setName("packetDropVector");
    packetDropVector.record(0);
    droppedCounter = 0;
}

void TransportRx::finish() {
}

void TransportRx::handleMessage(cMessage *msg) {

    // if msg is signaling an endServiceEvent
    if (msg == endServiceEvent) {
        
        // if packet in buffer, send next one
        if (!buffer.isEmpty()) {
            // dequeue packet
            cPacket *pkt = (cPacket*) buffer.pop();
            // send packet
            send(pkt, "toApp");
            // start new service
            // serviceTime = par("serviceTime");
            serviceTime = pkt->getDuration();
            scheduleAt(simTime() + serviceTime, endServiceEvent);
        }
    } else { // if msg is a packet

        if (msg->getKind() == 2) {
            // msg is a feedback packet
            fPacket* pkt = (fPacket*) msg;
            // Do something with the feedback info
            fPacket * chk = new fPacket("Tamaño actual de la ventana.");
            chk->setKind(2);
            chk->setRemainingBuffer((par("bufferSize").intValue() - buffer.getLength()));
            EV << "Tamaño actual de la ventana: " << chk->getRemainingBuffer() << endl;

            send(chk,"toOut$o");
            //delete(pkt); 
            //delete(msg); //? ¿Será necesario?
        }
        
        // msg is a data packet
        else {
                if (msg->getKind() == 1) {

                //if buffer is full, drop packet
                    if (buffer.getLength() >= par("bufferSize").intValue()) {
                    // drop the packet
                    delete(msg);
                    this->bubble("packet dropped");
                    droppedCounter ++;
                    packetDropVector.record(droppedCounter);
                }
            
                    // enqueue the packet
                    buffer.insert(msg);
                    bufferSizeVector.record(buffer.getLength());
                    // if the server is idle
                    if (!endServiceEvent->isScheduled()) {
                        // start the service now
                        scheduleAt(simTime() + 0, endServiceEvent);
                    }
                }
        }
    }
}

#endif /* TRANSPORTRX */


/*
    fPacket* pkt = new fPacket();
    pkt->setByteLength(20);
    pkt->setKind(2);
    pkt->setRemainingBuffer(par("bufferSize").intValue() - buffer.getLength());
    send(pkt, "toOut$o");

*/
