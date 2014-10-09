KOBE-an autoscaling agent
========

# background
Our project is a platform based on OpenStack and do some improvement and difference, such as hybrid cloud, monitor, security..
Because time is limited, i write an uglyyy autoscaling agent to finish the goal of autoscaling function. And i put some interface for lifecycle of the instances, both private and public. I assume amazon ec2 is the default public cloud.Next step i will refine the code and do some improvement.

# functions
- judge the monitor data whether it is reach the threshold and execute the action, but now the monitor data is only get by calculating the average of the instances of the specific group.It must be change, but i have not decided how.
- it can scale down as well as scale up, and i have an idea that i can make the instances number range from the workload in some specific period, which i think is the core of the cloud.
- i use haproxy as loadbalancer, and can put the instances into the autoscaling group automatic, but now it's only a testing function.

# about
His name is kobe...
