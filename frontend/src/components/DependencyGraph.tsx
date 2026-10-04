
import { useEffect, useMemo, useState } from 'react'
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  Position,
  type Edge,
  type Node,
} from '@xyflow/react'

import '@xyflow/react/dist/style.css'

type DependencyNode = {
  id: string
  label: string
}

type DependencyEdge = {
  source: string
  target: string
}

type DependencyGraphResponse = {
  status: string
  nodes: DependencyNode[]
  edges: DependencyEdge[]
}

type DependencyGraphProps = {
  repositoryPath?: string
}

const NODE_WIDTH = 210
const NODE_HEIGHT = 58

const COLUMN_GAP = 100
const ROW_GAP = 55

const GROUP_GAP = 90

function normalizePath(path: string) {
  return path.replaceAll('\\', '/')
}

function getFileName(path: string) {
  const parts = normalizePath(path)
    .split('/')
    .filter(Boolean)

  return parts[parts.length - 1] ?? path
}

function getGroupName(path: string) {
  const parts = normalizePath(path)
    .split('/')
    .filter(Boolean)

  if (parts.length <= 1) {
    return 'ROOT'
  }

  return parts[0]
}

function getNodeLabel(nodeId: string) {
  const parts = normalizePath(nodeId)
    .split('/')
    .filter(Boolean)

  if (parts.length >= 2) {
    return `${parts[parts.length - 2]} / ${
      parts[parts.length - 1]
    }`
  }

  return parts[0] ?? nodeId
}

function getNodeStyle(nodeId: string) {
  const fileName = getFileName(nodeId)

  if (
    fileName === 'main.py' ||
    fileName === 'app.py' ||
    fileName === 'index.py'
  ) {
    return {
      background: '#08060d',
      color: '#ffffff',
      border: '2px solid #08060d',
    }
  }

  if (fileName === '__init__.py') {
    return {
      background: '#faf7ff',
      color: '#08060d',
      border: '1px solid #aa3bff',
    }
  }

  return {
    background: '#ffffff',
    color: '#08060d',
    border: '1px solid #dedce2',
  }
}

function createLayout(
  graphNodes: DependencyNode[],
  graphEdges: DependencyEdge[],
) {

  const groups = new Map<
    string,
    DependencyNode[]
  >()

  graphNodes.forEach((node) => {
    const groupName = getGroupName(node.id)

    if (!groups.has(groupName)) {
      groups.set(groupName, [])
    }

    groups.get(groupName)!.push(node)
  })

  const nodes: Node[] = []

  let currentX = 40

  groups.forEach(
    (groupNodes, groupName) => {
      const rows = Math.max(
        1,
        Math.ceil(
          groupNodes.length / 2,
        ),
      )

      const groupWidth =
        2 * NODE_WIDTH + COLUMN_GAP

      groupNodes.forEach(
        (node, index) => {
          const column = index % 2
          const row = Math.floor(
            index / 2,
          )

          nodes.push({
            id: node.id,

            position: {
              x:
                currentX +
                column *
                  (NODE_WIDTH +
                    COLUMN_GAP),

              y:
                70 +
                row *
                  (NODE_HEIGHT +
                    ROW_GAP),
            },

            data: {
              label:
                getNodeLabel(node.id),
            },

            sourcePosition:
              Position.Bottom,

            targetPosition:
              Position.Top,

            style: {
              width: NODE_WIDTH,
              height: NODE_HEIGHT,

              ...getNodeStyle(
                node.id,
              ),

              borderRadius: 10,

              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',

              padding: '0 10px',

              boxSizing:
                'border-box',

              fontSize: 13,
              fontWeight: 500,

              textAlign: 'center',

              overflow: 'hidden',

              boxShadow:
                '0 2px 8px rgba(0, 0, 0, 0.04)',
            },
          })
        },
      )

      
      nodes.push({
        id: `group-${groupName}`,

        position: {
          x: currentX,
          y: 15,
        },

        data: {
          label:
            groupName.toUpperCase(),
        },

        draggable: false,

        selectable: false,

        style: {
          width:
            groupWidth,

          height: 30,

          background:
            'transparent',

          border:
            'none',

          boxShadow:
            'none',

          fontSize: 12,

          fontWeight: 700,

          color: '#6b6375',

          display: 'flex',

          alignItems:
            'center',

          justifyContent:
            'flex-start',

          padding: 0,
        },
      })

      currentX +=
        groupWidth +
        GROUP_GAP
    },
  )

 

  const realNodeIds =
    new Set(
      graphNodes.map(
        (node) => node.id,
      ),
    )

  const edges: Edge[] =
    graphEdges
      .filter(
        (edge) =>
          realNodeIds.has(
            edge.source,
          ) &&
          realNodeIds.has(
            edge.target,
          ),
      )
      .map(
        (edge, index) => ({
          id: `edge-${index}`,

          source: edge.source,

          target: edge.target,

          type: 'smoothstep',

          animated: false,

          style: {
            strokeWidth: 1.2,
            opacity: 0.55,
          },
        }),
      )

  return {
    nodes,
    edges,
  }
}

function DependencyGraph({
  repositoryPath,
}: DependencyGraphProps) {
  const [graph, setGraph] =
    useState<DependencyGraphResponse | null>(
      null,
    )

  const [loading, setLoading] =
    useState(true)

  const [error, setError] =
    useState('')

  const [selectedNode, setSelectedNode] =
  useState<string | null>(null)

  useEffect(() => {
    const fetchDependencyGraph =
      async () => {
        try {
          setLoading(true)
          setError('')
          setGraph(null)

          if (!repositoryPath) {
            setLoading(false)
            return
          }

          const response =
            await fetch(
              `http://127.0.0.1:8000/api/dependency-analysis/graph/directory?directory_path=${encodeURIComponent(
                repositoryPath,
              )}&project_root=${encodeURIComponent(
                repositoryPath,
              )}`,
            )

          if (!response.ok) {
            throw new Error(
              'Failed to load dependency graph.',
            )
          }

          const data: DependencyGraphResponse =
            await response.json()

          if (
            data.status !==
            'success'
          ) {
            throw new Error(
              'Dependency graph analysis failed.',
            )
          }

          setGraph(data)
        } catch (err) {
          setError(
            err instanceof Error
              ? err.message
              : 'Unable to load dependency graph.',
          )
        } finally {
          setLoading(false)
        }
      }

    fetchDependencyGraph()
  }, [repositoryPath])

  const layout = useMemo(() => {
    if (!graph) {
      return {
        nodes: [],
        edges: [],
      }
    }

    return createLayout(
      graph.nodes,
      graph.edges,
    )
  }, [graph])

  if (!repositoryPath) {
    return (
      <div className="dependency-graph">
        <p>
          Analyze a repository to
          view its dependency graph.
        </p>
      </div>
    )
  }

  if (loading) {
    return (
      <div className="dependency-graph">
        <p>
          Loading dependency
          graph...
        </p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="dependency-graph">
        <p>{error}</p>
      </div>
    )
  }

  if (
    !graph ||
    graph.nodes.length === 0
  ) {
    return (
      <div className="dependency-graph">
        <p>
          No dependency data
          found.
        </p>
      </div>
    )
  }

  
return (
  <div className="dependency-graph">
    <div className="dependency-graph-canvas">
      <ReactFlow
        nodes={layout.nodes}
        edges={layout.edges}
        onNodeClick={(_, node) => {
        console.log('NODE CLICKED:', node.id)
        setSelectedNode(node.id)
        }}
        fitView
        fitViewOptions={{
          padding: 0.15,
          maxZoom: 0.9,
        }}
        minZoom={0.15}
        maxZoom={1.5}
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>

    {selectedNode && (
      <div className="dependency-investigation-panel">
        <button
          className="dependency-panel-close"
          onClick={() => {
            setSelectedNode(null)
          }}
        >
          ×
        </button>

        <p className="dependency-panel-label">
          SELECTED FILE
        </p>

        <h3>
          {getFileName(selectedNode)}
        </h3>

        <p className="dependency-panel-path">
          {selectedNode}
        </p>

        <div className="dependency-panel-section">
          <p className="dependency-panel-label">
            DEPENDENCY ANALYSIS
          </p>

          <p>
            This file is part of the
            repository dependency graph.
          </p>
        </div>

        <div className="dependency-panel-section">
          <p className="dependency-panel-label">
            NEXT
          </p>

          <p>
            Git history and AI-based
            investigation will appear
            here later.
          </p>
        </div>
      </div>
    )}
    </div>
)
}

export default DependencyGraph
