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
