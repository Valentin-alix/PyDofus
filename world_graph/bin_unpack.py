import os
import sys
from pathlib import Path
from time import perf_counter

sys.path.append(os.path.dirname(Path(__file__).parent))
from const import DOFUS_PATH
from world_graph.byte_array import ByteArray
from world_graph.direction_enum import DirectionsEnum
from world_graph.edge import Edge
from world_graph.vertex import Vertex

PATH_WORLDGRAPH = os.path.join(DOFUS_PATH, "content", "maps", "world-graph.binary")


class WorldGraph:
    def __init__(self):
        self._vertices = dict[int, dict[int, Vertex]]()
        self._edges = dict[float, Edge]()
        self._outgoingEdges = dict[float, list[Edge]]()
        self._vertexUid: float = 0
        self.init()

    def init(self):
        s = perf_counter()
        with open(PATH_WORLDGRAPH, "rb") as binaries:
            data = ByteArray(binaries.read())
            edgeCount: int = data.readInt()
            for _ in range(edgeCount):
                src = self.addVertex(data.readDouble(), data.readInt())
                dest = self.addVertex(data.readDouble(), data.readInt())
                edge = self.addEdge(src, dest)
                transitionCount = data.readInt()
                for _ in range(transitionCount):
                    edge.addTransition(
                        data.readByte(),
                        data.readByte(),
                        data.readInt(),
                        data.readUTFBytes(data.readInt()),
                        data.readDouble(),
                        data.readInt(),
                        data.readDouble(),
                    )
            del data

    def addEdge(self, src: Vertex, dest: Vertex) -> Edge:
        edge: Edge = self._edges.get(src.UID, {}).get(dest.UID)
        if edge:
            return edge
        if not self.doesVertexExist(src) or not self.doesVertexExist(dest):
            return None
        edge = Edge(src, dest)
        if self._edges.get(src.UID) is None:
            self._edges[src.UID] = dict()
        self._edges[src.UID][dest.UID] = edge
        outgoing = self._outgoingEdges.get(src.UID)
        if outgoing is None:
            outgoing = list[Edge]()
            self._outgoingEdges[src.UID] = outgoing
        outgoing.append(edge)
        return edge

    def addVertex(self, mapId: float, zone: int) -> Vertex:
        vertex: Vertex = self._vertices.get(mapId, {}).get(zone)
        if vertex is None:
            vertex = Vertex(mapId, zone, self._vertexUid)
            self._vertexUid += 1
            if mapId not in self._vertices:
                self._vertices[mapId] = dict()
            self._vertices[mapId][zone] = vertex
        return vertex

    def doesVertexExist(self, v: Vertex) -> bool:
        return v.mapId in self._vertices and v.zoneId in self._vertices[v.mapId]

    def getEdges(self) -> dict:
        return self._edges

    def getVertex(self, mapId: float, mapRpZone: int) -> Vertex:
        mapId = float(mapId)
        mapRpZone = int(mapRpZone)
        return self._vertices.get(mapId, {}).get(mapRpZone)

    def getVertices(self, mapId) -> dict[int, Vertex]:
        return self._vertices[mapId]

    def getOutgoingEdgesFromVertex(self, src: Vertex) -> list[Edge] | None:
        if src is None:
            return None
        return self._outgoingEdges.get(src.UID, [])

    def getEdge(self, src: Vertex, dest: Vertex) -> Edge:
        return self._edges.get(src.UID, {}).get(dest.UID)

    def reset(self):
        self._vertices.clear()
        self._edges.clear()
        self._outgoingEdges.clear()
        self._vertexUid: float = 0

    def canChangeMap(self, mapId, direction):
        if not self.getVertices(mapId):
            return False
        for vertex in self.getVertices(mapId).values():
            for edge in WorldGraph().getOutgoingEdgesFromVertex(vertex):
                for transition in edge.transitions:
                    if (
                        transition.direction
                        and DirectionsEnum(transition.direction) == direction
                    ):
                        return True
        return False


if __name__ == "__main__":
    world_graph = WorldGraph()
    edges: dict[int, dict[int, Edge]] = world_graph.getEdges()

    edge = list(edges.values())[0][1]
    print(edge)
    # for edge in edges:
    #     print(edge)
