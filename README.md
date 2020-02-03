Work scheme:


```

res_req_script = jenkins-request-resources.sh (create file with task metadata in waiting queue, and check for it existance for specified interval.)
res_rej_script = jenkins-reject-resources.sh (delete file with task metadata in both queues, if something went wrong.)
return result = clusters ready to create task, and we can start build.


        +-return result --> jenkins                             automation dispatcher polling <--+
        |                     |                                           |                      |
        |        execute script(res_req_script)                 check for clusters workload      |
        |                     |                                           |                      |
        |        create file in dispatcher queue ---+           if workload < thresholds         |
        |                     |                     |                     |                      |
        |        check if file exists  <--+         |   +-----> get task from queue              |
        |                     |           |         |   |                 |                      |
        +-----------no-- if exists --yes--+         |   |       move it to running queue --+     |
                             |                      |   |                                  |     |
                             |                      |   |                                  |     |
                             |                      \  /                                   |     |
                             +-------------------> waiting <--- Queue(/root/queue) ---> running  |
                                                                                           |     |
                                                                                           +-----+

```