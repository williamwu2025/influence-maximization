using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using System.Text;

namespace InfluenceMaximization
{
	public class CoordinateDescent
	{
		public Graph graph;
		public List<int> initNodes;
		public double init_c;
		public int batch_num;
		public double alpha;
		public int mH;
		public Bipartite bg;
		public List<double> C;
		public List<double> prob_edge;
        public List<int> x;

        public CoordinateDescent(Graph graph, Bipartite bg, List<int> initNodes, double init_c, int batch_num, double alpha, int mH)
        {
            this.graph = graph;
            this.initNodes = initNodes;
            this.init_c = init_c;
            this.batch_num = batch_num;
            this.alpha = alpha;
            this.mH = mH;
            this.bg = bg;
            this.x = new List<int>();
            foreach (int u in initNodes) {x.Add(u);}

            C = new List<double>();
            for (int i = 0; i < graph.numV; ++i) C.Add(init_c);

            prob_edge = new List<double>();
            for (int h = 0; h < bg.numS; ++h) {prob_edge.Add(1.0);}
        }

        public void ChangeAllocation(int u, double nc)
        {
            double oc = C[u];
            C[u] = nc;
            if (oc == 1.0)
            {
                foreach (int e in bg.V2S[u])
                {
                    double res = 1.0;
                    foreach (int f in bg.S2V[e]) res *= (1 - C[f]);
                    prob_edge[e] = res;
                }
            }
            else {foreach (int e in bg.V2S[u]) prob_edge[e] = prob_edge[e] / (1 - oc) * (1 - nc);}
        }

        public Tuple<List<int>, double> gs(double b, List<int> range)
        {
            HashSet<int> seeds = new HashSet<int>();
            List<int> seedSet = new List<int>();
            //CELF Algorithm
            PriorityQueue<VNode> pq = new PriorityQueue<VNode>(range.Count+1, new VNodeComparer());
            List<bool> update = new List<bool>();
            foreach (int u in range)
            {
                VNode node = new VNode(u, bg.numS);
                pq.Push(node);
            }
            for (int u = 0; u < bg.numV; ++u) update.Add(false);
            double total_gain = 0.0;
            while (b > 0.0 && pq.Count>0)
            {
                for (int u = 0; u < bg.numV; ++u) update[u]=false;
                int next = 0;
                double gain = 0;
                while (true)
                {
                    VNode node = pq.Pop();
                    int max_u = node.id;
                    if (update[max_u])
                    {
                        next = max_u;
                        gain = node.val;
                        break;
                    }
                    else
                    {
                        double sum = 0;
                        foreach (int sid in bg.V2S[max_u]) sum += prob_edge[sid];
                        VNode n1 = new VNode(max_u, sum);
                        pq.Push(n1);
                        update[max_u] = true;
                    }
                }
                b -= 1.0;
                total_gain += gain;
                ChangeAllocation(next, 1.0);
                seeds.Add(next);
                seedSet.Add(next);
            }
            foreach (int point in seedSet) ChangeAllocation(point, 0.0);
            return new Tuple<List<int>, double>(seedSet, total_gain * bg.numV / bg.numS);
        }
    }
}