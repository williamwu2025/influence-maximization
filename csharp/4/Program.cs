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
            StreamReader initial = new StreamReader(filepath+"_ini100.txt");
            StreamReader nodetype = new StreamReader(filepath + "_typeo.txt");
            List<int> type = new List<int>();
            for (int i = 0; i < graph.numV; i++)
            {
                int flag = int.Parse(nodetype.ReadLine());
                if (flag == 0) { type.Add(0); }
                else if (flag == 1) { type.Add(2); }
                else { type.Add(1); }
            }
            List<int> seed = new List<int>();
            for (int i = 0; i < 100; i++) { seed.Add(int.Parse(initial.ReadLine()));}
            int mh = 0;
            if (filepath.Contains("Wiki")){mh = 250000;}
            else if (filepath.Contains("CA")) { mh = 2000000; }
            else if (filepath.Contains("dblp")) { mh = 20000000; }
            else { mh = 40000000; }
            double alpha = 0.6; // Step of c of searching the best discount in th Unified Discount Algorithm
            while (alpha <= 0.6)
            {
                Bipartite bg = new Bipartite(filepath, alpha, graph.numV);
                int b1 = 5;
                while (b1 <= 5)
                // Build a random hyper graph with mH random hyper edges.
                {
                    DateTime Hyper_start = DateTime.Now;
                    ICModel icm = new ICModel(alpha);
                    int count = Convert.ToInt16(1.5 * Convert.ToDouble(b1));
                    List<int> seed1 = graph.findlarge(seed, count);
                    CoordinateDescent cd1 = new CoordinateDescent(graph, bg, seed, seed1, 0.66667, type, 50, alpha, mh);
                    Random random = new Random();
                    int b2 = 25;
                    count = Convert.ToInt16(1.5 * Convert.ToDouble(b2));
                    int i1 = 0;
                    while (i1 < 5)
                    {
                        i1++;
                        int i = seed1[random.Next(0, seed1.Count)];
                        if (Math.Abs(1.0 - cd1.C[i]) < GlobalVar.epsilon) continue;
                        int j = seed1[random.Next(0, seed1.Count)];
                        if ((i == j) || Math.Abs(1.0-cd1.C[j])<GlobalVar.epsilon) continue;
                        double bp = cd1.C[i] + cd1.C[j];
                        double left = (bp - 1 > 0.0) ? (bp - 1) : 0.0;
                        double right = (bp < 1.0) ? bp : 1.0;
                        if (left >= right) continue;
                        double sumns = 0.0, sumnsi = 0.0, sumnsj = 0.0, sumnsij = 0.0;
                        for (int i2 = 0; i2 < 5; i2++)
                        {
                            List<int> realize = new List<int>();
                            foreach (int u in seed1)
                            {
                                if ((u == i) || (u == j)) continue;
                                if (random.NextDouble() < cd1.SeedProb(u, cd1.C[u])) { realize.Add(u); }
                            }
                            List<int> ns = graph.newreach(realize, seed);
                            List<int> seed2 = graph.findlarge(ns, count);
                            CoordinateDescent cd2 = new CoordinateDescent(graph, bg, ns, seed2, 0.66667, type, 10, alpha, mh);
                            List<double> cns = cd2.IterativeMinimize();
                            double qns = cd2.expectation();
                            sumns += qns;

                            realize.Add(i);
                            ns = graph.newreach(realize, seed);
                            seed2 = graph.findlarge(ns, count);
                            cd2 = new CoordinateDescent(graph, bg, ns, seed2, cns, type, 10, alpha, mh);
                            List<double> cnsi = cd2.IterativeMinimize();
                            double qnsi = cd2.expectation();
                            sumnsi += qnsi;

                            realize.Remove(i); realize.Add(j);
                            ns = graph.newreach(realize, seed);
                            seed2 = graph.findlarge(ns, count);
                            cd2 = new CoordinateDescent(graph, bg, ns, seed2, cns, type, 10, alpha, mh);
                            List<double> cnsj = cd2.IterativeMinimize();
                            double qnsj = cd2.expectation();
                            sumnsj += qnsj;

                            realize.Add(i);
                            ns = graph.newreach(realize, seed);
                            seed2 = graph.findlarge(ns, count);
                            if (qnsi > qnsj) { cd2 = new CoordinateDescent(graph, bg, ns, seed2, cnsi, type, 10, alpha, mh); }
                            else { cd2 = new CoordinateDescent(graph, bg, ns, seed2, cnsj, type, 10, alpha, mh); }
                            List<double> cnsij = cd2.IterativeMinimize();
                            double qnsij = cd2.expectation();
                            sumnsij += qnsij;
                        }
                        cd1.PairMinimize(i, j, sumnsi-sumns, sumnsi-sumns, sumns+sumnsij-sumnsi-sumnsj, bp, left, right);
                    }
                    DateTime Hyper_end = DateTime.Now;
                    double Hyper_time = (Hyper_end - Hyper_start).TotalMilliseconds;

                    Hyper_start = DateTime.Now;
                    seed1 = cd1.Realize();
                    List<int> nx = graph.newreach(seed1, seed);
                    List<int> s = graph.findlarge(nx, count);
                    CoordinateDescent cd = new CoordinateDescent(graph, bg, nx, s, 0.6667, type, 10, alpha, mh);
                    cd.IterativeMinimize();
                    List<double> prob = new List<double>();
                    for (int i = 0; i < nx.Count; i++) { prob.Add(cd.SeedProb(nx[i], cd.C[nx[i]])); }
                    Tuple<double, double> results = icm.InfluenceSpread(graph, nx, prob, 200);
                    Hyper_end = DateTime.Now;
                    FileStream outfile = new FileStream(filepath+"_4o.txt", FileMode.Append);
                    StreamWriter writer = new StreamWriter(outfile);
                    writer.Write("Choose time:" + Hyper_time + "\t");
                    Hyper_time = (Hyper_end - Hyper_start).TotalMilliseconds;
                    string mem = Convert.ToString(Process.GetCurrentProcess().WorkingSet64/8/1024/1024);
                    writer.Write("Propagation time:" + Hyper_time + "\t");
                    writer.Write("a:" + alpha + "\tb:" + (b1+b2) + "\tave:" + results.Item1 + "\tstd:" + results.Item2+"\tmemory:"+mem+"\n");
                    writer.Flush();
                    writer.Close();
                    b1 += 2;
                }
                alpha += 0.0;
            }
        }
    }
}
