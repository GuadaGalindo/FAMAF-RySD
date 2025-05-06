simple App
{
    parameters:
        volatile double interArrivalTime = default(0); // sec
        int packetByteSize = default(125); // bytes
        int destination = default(0);
        @display("i=block/app");
    gates:
        inout toNet;
}

simple Net
{
    parameters:
        @display("i=block/dispatch");
    gates:
        inout toApp;
        inout toLnk[];
}

simple Lnk
{
    parameters:
        @display("i=block/queue");
    gates:
        inout toNet;
        inout toOut;
}

module Node
{
    parameters:
        @display("i=block/routing");
        int interfaces;
    gates:
        inout toNod[interfaces];
    submodules:
        app: App {
            parameters:
                @display("p=75,50");
        }
        net: Net {
            parameters:
                @display("p=75,120");
        }
        lnk[interfaces]: Lnk {
            parameters:
                @display("p=75,190,r,70");
        }
    connections allowunconnected:
        app.toNet <--> net.toApp;
        for i=0..interfaces-1 {
            net.toLnk++ <--> lnk[i].toNet;
            lnk[i].toOut <--> toNod[i];
        }
}

network Network
{
    submodules:
        node[8]: Node {
            @display("p=100,100,ri,100,100");
            interfaces=2;
        }
    connections allowunconnected:
        node[0].toNod[1] <--> {  datarate = 1Mbps; delay = 100us; } <--> node[1].toNod[0];
        node[1].toNod[1] <--> {  datarate = 1Mbps; delay = 100us; } <--> node[2].toNod[0];
        node[2].toNod[1] <--> {  datarate = 1Mbps; delay = 100us; } <--> node[3].toNod[0];
        node[3].toNod[1] <--> {  datarate = 1Mbps; delay = 100us; } <--> node[4].toNod[0];
        node[4].toNod[1] <--> {  datarate = 1Mbps; delay = 100us; } <--> node[5].toNod[0];
        node[5].toNod[1] <--> {  datarate = 1Mbps; delay = 100us; } <--> node[6].toNod[0];
        node[6].toNod[1] <--> {  datarate = 1Mbps; delay = 100us; } <--> node[7].toNod[0];
        node[7].toNod[1] <--> {  datarate = 1Mbps; delay = 100us; } <--> node[0].toNod[0];
}