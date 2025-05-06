#ifndef NET
#define NET

#include <map>
#include <list>
#include <string.h>
#include <omnetpp.h>
#include <packet_m.h>
#include <hello_m.h>

using namespace omnetpp;

struct s_table {
    int counter = 0;
    std::list<int> sequenceSeen;
};

using table = s_table *; 

class Net: public cSimpleModule {
private:
    std::map <int, table> routingTable;
    cOutVector hopVector;
    cOutVector deadPackets;
    cOutVector dupPackets;
    cStdDev lnk0Used;
    cStdDev lnk1Used;
    int duplicatePacketCounter = 0;
    int deadPacketCounter = 0;

public:
    Net();
    virtual ~Net();
protected:
    virtual void initialize();
    virtual void finish();
    virtual void handleMessage(cMessage *msg);
    int ringSize;
};

Define_Module(Net);

#endif /* NET */

Net::Net() {
}

Net::~Net() {
}

void Net::finish() {
    recordScalar("Link 0 used", lnk0Used.getCount());
    recordScalar("Link 1 used", lnk1Used.getCount());
}

void Net::initialize() {
    hopVector.setName("Hop count");
    dupPackets.setName("Duplicate packets received");
    dupPackets.record(0);
    deadPackets.setName("Dead Packets");
    deadPackets.record(0);
    lnk0Used.setName("Link 0 used");
    lnk1Used.setName("Link 1 used");

    // Discover the size of the ring
    Hello *pkt = new Hello("discoverPacket");
    pkt->setSource(this->getParentModule()->getIndex());
    pkt->setDepth(1);
    pkt->setKind(1);
    pkt->setChannelSent(0);
    ringSize = 0;
    send(pkt, "toLnk$o", 0);    // Send to link interface #0 (clockwise side of the ring)
}

static bool alreadySeen(std::list<int> sequenceSeen, int sequence) {
    for (std::list<int>::iterator it = sequenceSeen.begin(); it != sequenceSeen.end(); ++it) {
        if (*it == sequence){
            return true;
        }
    }
    return false;
}

static int calculateCounter(std::list<int> sequenceSeen, int counter) {
    int newCounter = counter;
    for (std::list<int>::iterator it = sequenceSeen.begin(); it != sequenceSeen.end(); ++it) {
        if (*it == newCounter){
            newCounter++;
        }
    }
    return newCounter;
}

void Net::handleMessage(cMessage *msg) {

    // All msg (events) on net are packets
    Packet *pkt = (Packet *) msg;

    // Handle Hello packet
    if (pkt->getKind() == 1) {                  
        Hello * hello = (Hello *) msg;
        if (hello->getSource() == this->getParentModule()->getIndex()){
            // Update ring size
            ringSize = hello->getDepth();
            send(msg, "toApp$o");
        }
        else {
            hello->setDepth(hello->getDepth()+1);
            send(hello, "toLnk$o", 0);    // Send in clockwise direction                
        }    
    }

    // Data packet handling
    else if (pkt->getKind() == 2) {
    // If this node is the final destination, send to App
        if (pkt->getDestination() == this->getParentModule()->getIndex()) {
            int sequence = pkt->getSequenceNumber();

            // If it is the first time we see this source, add it to the routing table
            if (routingTable.find(pkt->getSource()) == routingTable.end()) {
                table newTable = new s_table;
                newTable->sequenceSeen.push_back(pkt->getSequenceNumber());
                routingTable.insert(std::pair<int, table>(pkt->getSource(), newTable));
            }
            
            // If we have seen this source before, check if the sequence number is higher
            else {
                
                table t = (routingTable.find(pkt->getSource()))->second;
                if (t->counter >= sequence || alreadySeen(t->sequenceSeen, sequence)){
                    duplicatePacketCounter++;
                    dupPackets.record(duplicatePacketCounter);
                    delete pkt;
                }
                else {
                    t->sequenceSeen.push_back(sequence);
                    t->sequenceSeen.sort();
                    t->counter = calculateCounter(t->sequenceSeen, t->counter);
                    
                    hopVector.record((ringSize/2) + (ringSize % 2) - pkt->getHopCount());
                    send(msg, "toApp$o");
                }
            }
        }

    // If not, send to the next node using the shortest path
        else {
            int chSent = pkt->getChannelSent();

            // Duplicate packet and send to both channels
            if (chSent == 2) {
                Packet * otherPkt = pkt->dup();
                otherPkt->setChannelSent(0);
                lnk0Used.collect(1);
                send(otherPkt, "toLnk$o", 0);
                pkt->setChannelSent(1);
                lnk1Used.collect(1);
                send(pkt, "toLnk$o", 1);
            }

            // Delete if hop count is 0 and send to the other channel if not
            else {
                if (pkt->getHopCount() == 0) {
                    bubble("packed died :C");
                    deadPacketCounter++;
                    deadPackets.record(deadPacketCounter);
                    delete pkt;
                }
                else {
                    pkt->setHopCount(pkt->getHopCount() - 1);
                    if(chSent == 0){
                        lnk0Used.collect(1);
                    }
                    else {
                        lnk1Used.collect(1);
                    }
                    send(pkt, "toLnk$o", chSent);
                }
            }
        }
    }
}
