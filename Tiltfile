allow_k8s_contexts('moky')
load('ext://file_sync_only', 'file_sync_only')

k8s_kind('LeaderWorkerSet', image_json_path=[
  '{.spec.leaderWorkerTemplate.leaderTemplate.spec.containers[0].image}',
  '{.spec.leaderWorkerTemplate.workerTemplate.spec.containers[0].image}',
])
file_sync_only("ghcr.io/abatilo/butterfly:latest",
    "./dev.yaml",
    live_update=[
        sync("./", "/workspace/butterfly"),
    ],
)
