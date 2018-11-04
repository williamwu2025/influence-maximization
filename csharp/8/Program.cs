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
        public static string filepath = "/home/sjtuiiot/wcy/im/soc-LiveJournal1";
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
            double alpha = 1.0; // Step of c of searching the best discount in th Unified Discount Algorithm
            while (alpha <= 1.0)
            {
                Bipartite bg = new Bipartite(filepath, alpha, graph.numV);
                double b = 10.0;
                while (b <= 10.0)
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
                        List<int> bestseed = new List<int>();
                        List<double> bestallo = new List<double>();
                        foreach (int u in seed)
                        {
                            List<int> nrlist = graph.newreach(new List<int> {u}, cd.x);
                            double b2cub1 = 5 * cu[u];
                            if (b2cub1 >= 0.5 && nrlist.Count>=1)
                            {
                                Tuple<List<int>, List<double>, double> result1 = cd.bestone(nrlist,b2cub1);
                                if (result1.Item3/cu[u] >= maxE/cu[flag])
                                {
                                    maxE = result1.Item3;
                                    flag = u;
                                    bestseed = new List<int>();
                                    foreach (int point in result1.Item1) bestseed.Add(point);
                                    bestallo = new List<double>();
                                    foreach (double resource in result1.Item2) bestallo.Add(resource);
                                }
                            }
                            if (b2cub1>=1.0 && nrlist.Count>=2)
                            {
                                Tuple<List<int>, List<double>, double> result2 = cd.besttwo(nrlist, b2cub1);
                                if (result2.Item3 / cu[u] >= maxE / cu[flag])
                                {
                                    maxE = result2.Item3;
                                    flag = u;
                                    bestseed = new List<int>();
                                    foreach (int point in result2.Item1) bestseed.Add(point);
                                    bestallo = new List<double>();
                                    foreach (double resource in result2.Item2) bestallo.Add(resource);
                                }
                            }
                            if (b2cub1 >= 1.5 && nrlist.Count>=3)
                            {
                                Tuple<List<int>, List<double>, double> result3 = cd.bestone(nrlist, b2cub1);
                                if (result3.Item3 / cu[u] >= maxE / cu[flag])
                                {
                                    maxE = result3.Item3;
                                    flag = u;
                                    bestseed = new List<int>();
                                    foreach (int point in result3.Item1) bestseed.Add(point);
                                    bestallo = new List<double>();
                                    foreach (double resource in result3.Item2) bestallo.Add(resource);
                                }
                            }
                        }
                        if (bused+cu[flag] > b) break;
                        bused += cu[flag];
                        seed.Remove(flag);
                        List<int> maxnr = graph.newreach(new List<int>{flag}, cd.x);
                        for (int u = 0;u<bestseed.Count;u++)
                        {
                            if (bused+bestallo[u] > b) break;
                            cd.ChangeAllocation(bestseed[u], bestallo[u]);
                            cd.x.Add(bestseed[u]);
                            bused += bestallo[u];
                        }
                        Console.WriteLine("newreach:"+Convert.ToString(cd.C.Sum())+"total:"+Convert.ToString(bused));
                    }
                    DateTime Hyper_end = DateTime.Now;
                    double Hyper_time = (Hyper_end - Hyper_start).TotalMilliseconds;

                    Hyper_start = DateTime.Now;
                    List<double> prob = new List<double>();
                    foreach (int u in cd.x) { prob.Add(cd.SeedProb(u, cd.C[u])); }
                    Tuple<double, double> results = icm.InfluenceSpread(graph, cd.x, prob, 200);
                    Hyper_end = DateTime.Now;
                    FileStream outfile = new FileStream(filepath+"_8o.txt", FileMode.Append);
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
