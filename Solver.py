# settings from https://www.sciencedirect.com/science/article/pii/S0167739X18321332

# setting for cloud
cloud_proc_rate = 10 # GHz
cloud_proc_cost = 0.5
cloud_bandwidth = 500 # Mbps
cloud_comm_cost = 0.5

# setting for edge
local_proc_rate = 1 # GHz
local_proc_cost = 0.3
local_bandwidth = 1000 # Mbps
local_comm_cost = 0.7
#========================================================

import logging
import queue
from re import L
from tabnanny import check

class Solver(object):
    def __init__(self, ):
        logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        pass
    
    def mounting_data(self, task_unit):
        self.TASK_local=task_unit[0][0]
        self.TASK_cycles=task_unit[1][0]
        self.EDGE_src=task_unit[2][0]
        self.EDGE_dst=task_unit[3][0]
        self.EDGE_bits=task_unit[4][0] #(kb)
        self.LOCAL=task_unit[5][0]
        self.LOCperm=task_unit[6][0] #(Mhz)

        #  reset index
        for i in range(0,len(self.TASK_local)):
            self.TASK_local[i]-=1
        for i in range(0,len(self.EDGE_src)):
            self.EDGE_src[i]-=1
            self.EDGE_dst[i]-=1
        # create graph
        self.TASK_num=len(self.TASK_cycles)
        self.Graph=[]
        for i in range(0,self.TASK_num):
            self.Graph.append([])
        for i in range(0,len(self.EDGE_dst)):
            self.Graph[self.EDGE_src[i]].append([self.EDGE_dst[i],self.EDGE_bits[i]])

    def debugger(self):
        try:
            print(self.LOCperm)
        except BaseException:
            self.logger.info("taskinfo miss!")

    ###################################################################
    # baseline
    ###################################################################
    # 为枚举的状态计算结果
    # state=0 即所有任务均在本地计算 
    def check_state(self, state=0):
        stime = [.0]*self.TASK_num
        ftime = [.0]*self.TASK_num
        cost = [.0]*self.TASK_num
        #count for degree
        degree_in = [0]*self.TASK_num
        for it in self.EDGE_dst:
            degree_in[it]+=1
        #topo order
        q = queue.Queue()
        q.put(0)
        stime[0]= .0
        while (not q.empty()):
            u = q.get()
            #任务计算时间
            if ((state>>u)&1)==0:
                # ptime = self.TASK_cycles[u] * 1e6 / (envconfig.local_proc_rate * 1e9)
                ptime = self.TASK_cycles[u] / local_proc_rate / 1e3
                cost[u] =ptime *local_proc_cost
            elif ((state>>u)&1)==1:
                ptime = self.TASK_cycles[u] / cloud_proc_rate / 1e3
                cost[u] =ptime * cloud_proc_cost
            ftime[u] = stime[u] + ptime
            
            
            for vv in self.Graph[u]:
                v , bits = vv[0],vv[1]
                # 传输时延
                comm_time = 0.0
                if ((state>>u)&1) != ((state>>v)&1):
                    if (state>>u&1)==0:
                        # 本地服务器上传时延
                        comm_time = 1.0 * bits / cloud_bandwidth / 1e3
                    elif (state>>u&1)==1:
                        # 云服务器下发时延
                        # comm_time = (bits * 1e3) / (envconfig.local_bandwidth *1e6)
                        comm_time = 1.0 * bits / local_bandwidth / 1e3
                    else:
                        comm_time = 0.0

                # 后继结点开始时间为所有前驱结点结束时间加上传输时延的最大值
                stime[v]=max(stime[v], ftime[u] + comm_time)
                # 后继节点花费为所有前驱结点花费加上传输花费的总和
                cost[v]+= cost[u]
                degree_in[v]-=1
                if degree_in[v]==0:
                    q.put(v)
        return ftime[self.TASK_num-1]   

    # 搜索所有状态
    def solve_search(self):
        result = []
        for state in range(0,(1<<self.TASK_num)-1):
            # 检测状态是否合法
            fail_flag = 0
            for i in range(0,self.TASK_num):
                if self.LOCAL[i]==1 and (state>>i)&1==1:
                    fail_flag = 1
                    break
            if fail_flag == 0:
                result.append(self.check_state(state))
        return min(result)

    ###################################################################
    # dp-method
    ###################################################################
    def solve_dp(self):
        ################ phase1 ################
        taskorder = []
        # count for degree
        degree_in = [0]*self.TASK_num
        for it in self.EDGE_dst:
            degree_in[it]+=1
        # topo order
        q = queue.Queue()
        q.put(0)
        while (not q.empty()):
            u = q.get()
            taskorder.append(u)
            for vv in self.Graph[u]:
                v = vv[0]
                degree_in[v]-=1
                if degree_in[v]==0:
                    q.put(v)
        # print(taskorder)

        ################ phase2 ################
        tr = [.0]*self.TASK_num
        tl = [.0]*self.TASK_num
        for u in range(0,self.TASK_num):
            tl[u] += self.TASK_cycles[u] / local_proc_rate / 1e3
            tr[u] += self.TASK_cycles[u] / cloud_proc_rate / 1e3
            if self.LOCAL[u]==1:
                tr[u] = 1e18

            for vv in self.Graph[u]:
                v , bits = vv[0],vv[1]
                comm_time = 1.0 * bits / local_bandwidth / 1e3
                tl[v] = max(tl[v], min(tl[u], tr[u] + comm_time))
                if self.LOCAL[v]==1:
                    continue
                comm_time = 1.0 * bits / cloud_bandwidth / 1e3
                tr[v] = max(tr[v], min(tl[u] + comm_time, tr[u]))
        return tl[self.TASK_num-1]
