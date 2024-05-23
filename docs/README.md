# Documentation

This folder should contain your documentation, explaining the structure and content of your project. It should also contain your diagrams, explaining the architecture. The recommended writing format is Markdown.

## Architecture diagram
![](ArchitectureDiagram.png)


## System diagram

![](SystemDiagram.JPG)

## Vector clock diagram

### Successful order
All of the caches are cleared automatically, once a microservice returns its result to the Orchestrator.
![](VectorDiagramPass.png)

### Failed order
If any check is failed, the service will notify all other services. All microservices will return a default answer, and the cache is cleared everywhere.
![](VectorDiagramFail.png)


## Leader election

### Lock-based leader election
All the executors are trying to acquire the lock. The first one to acquire it becomes the leader. After the lock times out (current ttl=10) others can try to acquire it.
![](LeaderElectionDiagram.PNG)

## Database Replication

The replication of database uses a Remote-write primary-based protocol where the primary server is being chosen by continuous leader elections

![](DBReplicationDiagram.PNG)

## Distributed Commitment Protocol

![](commitment_diagram.png)

## Final architecture diagram
![](Final_Architecture.png)

## Grafana dashboard
![](Grafana.png)
