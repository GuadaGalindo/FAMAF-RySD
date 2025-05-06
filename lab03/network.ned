simple Generator
{
    parameters:
        int packetByteSize;
        volatile double generationInterval; // sec
        @display("i=block/source");
    gates:
        output out;
}

simple Queue
{
    parameters:
        volatile double serviceTime; // sec
        int bufferSize;
        @display("i=block/queue;q=buffer");
    gates:
        input in;
        output out;
}

simple Sink
{
    parameters:
        @display("i=block/sink");
    gates:
        input in;
}

simple TransportTx
{
    parameters:
        int bufferSize;
        int packetByteSize;
        volatile double generationInterval;
        @display("i=block/queue;q=buffer");
    gates:
        input toApp;
        inout toOut;
}

simple TransportRx
{
    parameters:
        int bufferSize;
        @display("i=block/queue;q=buffer");
    gates:
        output toApp;
        inout toOut;
}

module NodeTx
{
    parameters:
        @display("i=block/routing");
    gates:
        input in;
        output out;
    submodules:
        gen: Generator {
            parameters:
                @display("p=75,178");
        }
        traTx: TransportTx {
            parameters:
                @display("p=75,94");
        }
    connections:
        in --> traTx.toOut$i;
        gen.out --> traTx.toApp;
        traTx.toOut$o --> out;
}

module NodeRx
{
    parameters:
        @display("i=block/routing");
    gates:
        input in;
        output out;
    submodules:
        sink: Sink {
            parameters:
                @display("p=75,137");
        }
        traRx: TransportRx {
            parameters:
                @display("p=75,227");
        }
    connections:
        in --> traRx.toOut$i;
        traRx.toOut$o --> out;
        //case study 1;
        traRx.toApp --> {  datarate = 0.5Mbps; } --> sink.in;
        //case study 2;
        // traRx.toApp --> { datarate = 1Mbps; } --> sink.in;
}

network Network
{
    @display("bgl=2");
    submodules:
        nodeTx: NodeTx {
            @display("p=30,30");
        }
        queue1: Queue {
            @display("p=130,30");
        }
        nodeRx: NodeRx {
            @display("p=230,30");
        }
        queue2: Queue {
            @display("p=130,128");
        }
    connections:
        nodeTx.out --> {  datarate = 1Mbps; delay = 100us; } --> queue1.in;
        //case study 1;
        queue1.out --> {  datarate = 1Mbps; delay = 100us; } --> nodeRx.in;
        //case study 2;
        //queue1.out --> { datarate = 0.5Mbps; delay = 100us; } --> nodeRx.in;


        nodeRx.out --> {  datarate = 1Mbps; delay = 100us; } --> queue2.in;
        //case study 1;
        queue2.out --> {  datarate = 1Mbps; delay = 100us; } --> nodeTx.in;
        //case study 2;
        //queue2.out --> {  datarate = 0.5Mbps; delay = 100us; } --> nodeTx.in;
}
