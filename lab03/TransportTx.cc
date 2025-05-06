#ifndef TRANSPORTTX
#define TRANSPORTTX

#include <string.h>
#include <omnetpp.h>
#include "packet_m.h"

using namespace omnetpp;

class TransportTx : public cSimpleModule {
    private:
        int remainingWindow;
        cQueue buffer;
        cMessage *endServiceEvent;
        simtime_t serviceTime;
        cOutVector bufferSizeVector;
        cOutVector packetDropVector;
        int droppedCounter;
    public:
        TransportTx();
        virtual ~TransportTx();
    protected:
        virtual void initialize();
        virtual void finish();
        virtual void handleMessage(cMessage *msg);
};

Define_Module(TransportTx);

TransportTx::TransportTx() {
    endServiceEvent = NULL;
}

TransportTx::~TransportTx() {
    cancelAndDelete(endServiceEvent);
}

void TransportTx::initialize() {
    remainingWindow = 0;
    buffer.setName("buffer");
    endServiceEvent = new cMessage("endService");
    bufferSizeVector.setName("bufferSizeVector");
    packetDropVector.setName("packetDropVector");
    packetDropVector.record(0);
    droppedCounter = 0;
}

void TransportTx::finish() {
}

void TransportTx::handleMessage(cMessage *msg) {

    // if msg is signaling an endServiceEvent
    if (msg == endServiceEvent) {
        
        // if packet in buffer, send next one
        if (!buffer.isEmpty()) {

            if(remainingWindow <= 0){
                //crea el packete de control y lo envia
                EV << "Tamaño actual de la ventana (llena): " << remainingWindow << endl;
                fPacket * pkt = new fPacket("ventana actual llena");
                pkt->setKind(2);
                send(pkt, "toOut$o");
                // serviceTime = pkt->getDuration();
                // serviceTime = (serviceTime + (serviceTime * contScalar));
                // scheduleAt(simTime() + serviceTime, endServiceEvent);
                scheduleAt(simTime() + par("generationInterval"), endServiceEvent);
            }
            else {
                // dequeue packet
                cPacket *pkt = (cPacket*) buffer.pop();
                // send packet
                send(pkt, "toOut$o");
                remainingWindow --;
                // start new service
                // serviceTime = par("serviceTime");
                serviceTime = pkt->getDuration();
                scheduleAt(simTime() + serviceTime, endServiceEvent);
            }
        }

    } else {
        
        // if msg is a packet
        if (msg->getKind() == 2) {
            // msg is a feedback packet
            fPacket* pkt = (fPacket*) msg;
            // Do something with the feedback info
            remainingWindow = pkt->getRemainingBuffer();
            EV << "Tamaño de la ventana en Tx linea 91: " << remainingWindow << endl;
            
            // delete(pkt);
            // delete(msg); //? ¿Será necesario?
        }

        // msg is a data packet
        else {
            if (msg->getKind() == 1) {
                // if buffer is full, drop packet
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

#endif /* TRANSPORTTX */

