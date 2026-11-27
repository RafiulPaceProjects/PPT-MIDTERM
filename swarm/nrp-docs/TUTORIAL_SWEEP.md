# NRP Tutorial Sweep, 2026-11-27

Owner pointed at the tutorial introduction page and ordered a deep check through the
docs. Every page in the Tutorial section of https://nrp.ai/documentation/userdocs/
was read as a web page on 2026-11-27. The section holds exactly 8 pages, confirmed
against the documentation index in llms-full.txt. Three of them (introduction, basic,
storage) were already filed in the earlier NRP filing and were re-read here and
deduped. Five are new to the research-brain.

Workload lens for the extraction: a roughly 200M parameter vision-language model,
checkpoints near 800 MB, multi-hour runs, checkpointing every 30 minutes, one
researcher (rh43950n@pace.edu) on the hosted West hub, whose first A100 server is
pending with insufficient nvidia.com/gpu reported across the cluster.

## Pages read

1. Introduction, https://nrp.ai/documentation/userdocs/tutorial/introduction/
   The on-ramp: Nautilus is free for InCommon institutions under fair use, access
   takes five steps (account, local setup, promotion to user or admin, policies,
   tutorials), and JupyterLab is the no-Kubernetes path for people who do not want
   to learn the cluster tools first. Already filed earlier; re-read and deduped.

2. Basic Kubernetes Tutorial, https://nrp.ai/documentation/userdocs/tutorial/basic/
   kubectl basics and the first YAML: a pod with requests equal to limits (200Mi
   memory, 200m cpu), events and describe as the way to see what a pod is doing,
   the statelessness demonstration (files outside a volume vanish when the pod is
   deleted), and the same spec rebuilt as a Deployment so the cluster restarts it.
   Already filed earlier; re-read and deduped.

3. Scheduling and Exposing, https://nrp.ai/documentation/userdocs/tutorial/basic2/
   NEW. A two-replica Apache Deployment behind a load-balancing Service, exposed
   to the internet through an Ingress. Carries the sizing warning used in the
   filing: asking for too many resources decreases the chances the cluster can
   provide them in a reasonable timeframe, and asking for too few hurts the work.

4. Docker and Kubernetes, https://nrp.ai/documentation/userdocs/tutorial/docker/
   NEW. Local Docker lesson: derive an image from a pinned tag (python:3.9 in the
   example, never silent latest), keep build steps in one RUN layer, and push the
   image to Docker Hub or the NRP GitLab registry so the cluster can pull it. Data
   in a stopped container is lost unless it sits in a persistent volume.

5. Docker Images, https://nrp.ai/documentation/userdocs/tutorial/images/
   NEW. Extending or changing an existing image through the NRP GitLab build flow:
   add a Dockerfile to a GitLab project, make it public or pull a private image
   with a deploy token, then run the result using the basic tutorial pod.

6. Running Batch Jobs (tutorial), https://nrp.ai/documentation/userdocs/tutorial/jobs/
   NEW. The Job lesson: a batch/v1 Job watches its pod and restarts it on a
   non-zero exit up to backoffLimit times (example backoffLimit 4, restartPolicy
   Never). Long jobs can pass through Error and Evicted states. The finished Job
   and pod stay readable for ttlSecondsAfterFinished of 604800 seconds (1 week)
   by default, and that value can be set in the Job spec. Output goes to the pod
   logs through kubectl logs.

7. Scheduling Workloads in Nautilus, https://nrp.ai/documentation/userdocs/tutorial/scheduling/
   NEW, and the most useful page in the section for this workload. Node power is
   exposed through labels and users have list-only node access (get nodes, get
   nodes -L, get node -l; no describe node, no node yaml). A GPU is requested as
   nvidia.com/gpu with the same value in requests and limits; fractions of a GPU
   cannot be requested. A GPU model is pinned with required nodeAffinity on the
   nvidia.com/gpu.product label, or only preferred with preferred nodeAffinity
   and a weight, which lets the scheduler fall back to another model. Region and
   zone come from topology labels, so compute can be placed near storage. If a
   pod cannot be scheduled, the events list shows why; reserved nodes carry the
   NoSchedule taint nautilus.io/reservations and need a matching toleration with
   the reservation name as the value. The portal Resources page and
   nrp.ai/viz/resources show live node features and taints.

8. Storage, https://nrp.ai/documentation/userdocs/tutorial/storage/
   PVC lesson: a claim named test-vol on storageClassName rook-ceph-block,
   accessModes ReadWriteOnce, requests.storage 1Gi, wired into a pod through
   volumes.persistentVolumeClaim.claimName and volumeMounts.mountPath. Claims are
   scoped to one namespace. The emptyDir half repeats the scratch rule: more than
   50Gi of ephemeral writes can evict the pod, so requests.ephemeral-storage
   should cover the expected scratch. Already filed earlier; re-read and deduped.

## Not read, with reasons

- https://nrp.ai/sitemap.xml returns 404; the site publishes no sitemap. The
  tutorial tree was enumerated from llms-full.txt and the pages themselves
  instead.
- The Local Scratch and High I/O Jobs guides are linked from the storage
  tutorial but live in the storage section, not the tutorial section. They are
  named here as pointers for a later sweep; nothing in this note rests on them.
- No tutorial page failed to load. All 8 pages were read in full.

## What it teaches for the pending A100 and the Jobs route

- The pending server is a capacity wait, not a broken request. The spawn log
  (insufficient GPU on hundreds of nodes, preemption not helpful) matches the
  scheduling tutorial picture of a hard requirement meeting a busy cluster. The
  tutorials give no queue and no priority trick for an ordinary pod. The levers
  are waiting, softening a hard GPU requirement into a weighted preference, or
  running under a reservation with its toleration.
- Before the next GPU ask, check live availability with the label queries
  (kubectl get nodes -L nvidia.com/gpu.product) or the portal Resources page,
  and pick the requirement from what the cluster actually has free.
- The Job route inherits the tutorial numbers: backoffLimit restarts a failed
  pod, restartPolicy Never, records kept 1 week by default, results in the pod
  logs, and checkpoints belong on a namespace PVC wired by claimName and
  mountPath, sized by the claim, on the default rook-ceph-block class for a
  single pod.

## Filing record

Research-brain run 3c527ce8-9775-49d2-a2d5-039ba3c1164d, closed done, cost 0,
every write read back. Sources written: 5 (basic2, docker, images, jobs tutorial,
scheduling tutorial). Sources deduped: 3 (introduction, basic, storage).
Findings written: 6, all area platform (platform total now 19). Lessons written: 3
(prefer a GPU model before requiring it; read the events before changing the
spec; treat every resource request as a scheduling bid).
