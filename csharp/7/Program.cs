using System;
using System.IO;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Diagnostics;

namespace InfluenceMaximization
{
    class MainClass
    {
        public static string filepath = "/home/sjtuiiot/wcy/im/Wiki-Vote";
        //public static string filepath = "D:/iiot/csharp/im/Wiki-Vote";
        public static void Main(string[] args)
        {
            Graph graph = new Graph(filepath+".csv");
            
            CoordinateDescentAlgCommonHyperGraphOneAlpha(graph);
         }
        public static void CoordinateDescentAlgCommonHyperGraphOneAlpha(Graph graph)
        {
            StreamReader nodetype = new StreamReader(filepath + "_typeo.txt");
            StreamReader threshold = new StreamReader(filepath + "_tu.txt");
            List<double> thresh = new List<double>();
            for (int i = 0; i < graph.numV; i++) { thresh.Add(double.Parse(threshold.ReadLine()));}
            List<int> type = new List<int>();
            for (int i = 0; i < graph.numV; i++)
            {
                int flag = int.Parse(nodetype.ReadLine());
                if (flag == 0) { type.Add(0); }
                else if (flag == 1) { type.Add(2); }
                else { type.Add(1); }
            }
            List<double> d = new List<double>{ 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0};
            List<double> cu = new List<double>();
            for (int i = 0; i < graph.numV; i++)
            {
                //cu.Add(1.0);
                double t = thresh[i];
                double p = 0.0;
                if (type[i] == 1) { p = System.Math.Pow(t, 0.5); }
                else if (type[i] == 2) { p = t; }
                else { p = 1-System.Math.Pow(1-t, 0.5); }
                foreach( double point in d)
                {
                    if (point < p) continue;
                    cu.Add(point);
                    break;
                }
            }
            int mh = 0;
            if (filepath.Contains("Wiki")){mh = 250000;}
            else if (filepath.Contains("CA")) { mh = 2000000; }
            else if (filepath.Contains("dblp")) { mh = 20000000; }
            else { mh = 40000000; }
            double alpha = 0.6; // Step of c of searching the best discount in th Unified Discount Algorithm
            while (alpha <= 1.0)
            {
                Bipartite bg = new Bipartite(filepath, alpha, graph.numV);
                double b = 10.0;
                double ratio = 3.0;
                while (b <= 50.0)
                // Build a random hyper graph with mH random hyper edges.
                {
                    StreamReader initial = new StreamReader(filepath + "_ini100.txt");
                    List<int> seed = new List<int>();
                    for (int i = 0; i < 100; i++) { seed.Add(int.Parse(initial.ReadLine()));}
                    DateTime Hyper_start = DateTime.Now;
                    ICModel icm = new ICModel(alpha);
                    CoordinateDescent cd = new CoordinateDescent(graph, bg, seed, 0.0, type, 20, alpha, mh);
                    double bused = 0.0;
                    while (bused <= b)
                    {
                        int flag = seed[0];
                        double maxE = 0.0;
                        int circumstance = 0;
                        List<int> seedset = new List<int>();
                        foreach (int u in seed)
                        {
                            List<int> nrlist = graph.newreach(new List<int> {u}, cd.x);
                            double b2cub1 = ratio * cu[u];
                            Tuple<List<int>,double> choose = cd.gs(b2cub1, nrlist);
                            if (choose.Item2/cu[u] >= maxE/cu[flag])
                            {
                                maxE = choose.Item2;
                                flag = u;
                                seedset = new List<int>();
                                foreach (int point in choose.Item1) seedset.Add(point);
                                circumstance = 1;
                            }
                            b2cub1 = b2cub1 >= 1.0 ? 1.0 : b2cub1;
                            foreach(int v in nrlist)
                            {
                                double nowE = cd.singlepointgain(v, b2cub1);
                                if (nowE/cu[v] >= maxE/cu[flag])
                                {
                                    maxE = nowE;
                                    flag = u;
                                    seedset = new List<int> { v };
                                    circumstance = 2;
                                }
                            }
                        }
                        if (bused+cu[flag] > b) break;
                        bused += cu[flag];
                        seed.Remove(flag);
                        List<int> maxnr = graph.newreach(new List<int>{flag}, cd.x);
                        if (circumstance <= 2){
                            foreach (int u in seedset)
                            {
                                double allocation = 0.0;
                                if (type[u] == 1) allocation = 1.0; else allocation = 0.5;
                                //allocation = 1.0;
                                if (bused+allocation > b) break;
                                cd.ChangeAllocation(u, allocation);
                                cd.x.Add(u);
                                Console.Write(Convert.ToString(u)+" ");
                                bused += allocation;
                            }
                        }
                        else{
                            double allocation = cu[flag] * ratio;
                            allocation = allocation >= 1.0 ? 1.0 : allocation;
                            if (bused+allocation > b) break;
                            cd.ChangeAllocation(seedset[0], allocation);
                            cd.x.Add(seedset[0]);
                            Console.Write(Convert.ToString(seedset[0]) + "  ");
                            bused += allocation;
                        }
                        Console.WriteLine("newreach:"+Convert.ToString(cd.C.Sum())+"total:"+Convert.ToString(bused));
                    }
                    DateTime Hyper_end = DateTime.Now;
                    double Hyper_time = (Hyper_end - Hyper_start).TotalMilliseconds;
                    Console.WriteLine(cd.x.Count);

                    Hyper_start = DateTime.Now;
                    List<double> prob = new List<double>();
                    foreach (int u in cd.x) { prob.Add(cd.SeedProb(u, cd.C[u])); }
                    Tuple<double, double> results = icm.InfluenceSpread(graph, cd.x, prob, 200);
                    Hyper_end = DateTime.Now;
                    FileStream outfile = new FileStream(filepath+"_7o.txt", FileMode.Append);
                    StreamWriter writer = new StreamWriter(outfile);
                    writer.Write("Choose time:" + Hyper_time + "\t");
                    Hyper_time = (Hyper_end - Hyper_start).TotalMilliseconds;
                    string mem = Convert.ToString(Process.GetCurrentProcess().WorkingSet64/8/1024/1024);
                    writer.Write("Propagation time:" + Hyper_time + "\t");
                    writer.Write("a:" + alpha + "\tb:" + b + "\tave:" + results.Item1 + "\tstd:" + results.Item2+"\tmemory:"+mem+"\n");
                    writer.Flush();
                    writer.Close();
                    b += 10.0;
                }
                alpha += 0.2;
            }
        }
    }
}
