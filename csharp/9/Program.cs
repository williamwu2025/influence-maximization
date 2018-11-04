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
            int mh = 0;
            if (filepath.Contains("Wiki")){mh = 250000;}
            else if (filepath.Contains("CA")) { mh = 2000000; }
            else if (filepath.Contains("dblp")) { mh = 20000000; }
            else { mh = 40000000; }
            double alpha = 0.6; // Step of c of searching the best discount in th Unified Discount Algorithm
            while (alpha <= 0.6)
            {
                Bipartite bg = new Bipartite(filepath, alpha, graph.numV);
                double b = 10.0;
                double ratio = 4.0;
                while (b <= 50.0)
                // Build a random hyper graph with mH random hyper edges.
                {
                    StreamReader initial = new StreamReader(filepath + "_ini100.txt");
                    List<int> seed = new List<int>();
                    List<int> final = new List<int>();
                    for (int i = 0; i < 100; i++) { seed.Add(int.Parse(initial.ReadLine()));}
                    DateTime Hyper_start = DateTime.Now;
                    ICModel icm = new ICModel(alpha);
                    CoordinateDescent cd = new CoordinateDescent(graph, bg, seed, 0.0, 10, alpha, mh);
                    double bused = 0.0;
                    while (bused <= b)
                    {
                        int flag = seed[0];
                        double maxE = 0.0;
                        List<int> seedset = new List<int>();
                        foreach (int u in seed)
                        {
                            List<int> nrlist = graph.newreach(new List<int> {u}, cd.x);
                            double b2cub1 = ratio;
                            Tuple<List<int>,double> choose = cd.gs(b2cub1, nrlist);
                            if (choose.Item2 >= maxE)
                            {
                                maxE = choose.Item2;
                                flag = u;
                                seedset = new List<int>();
                                foreach (int point in choose.Item1) seedset.Add(point);
                            }
                        }
                        if (bused + 1.0 > b) break;
                        bused += 1.0;
                        seed.Remove(flag);
                        foreach (int u in seedset)
                        {
                            if (bused + 1.0 > b) break;
                            cd.ChangeAllocation(u, 1.0);
                            cd.x.Add(u);
                            final.Add(u);
                            Console.Write(Convert.ToString(u)+" ");
                            bused += 1.0;
                        }
                        Console.WriteLine("newreach:"+Convert.ToString(cd.C.Sum())+"total:"+Convert.ToString(bused));
                    }
                    DateTime Hyper_end = DateTime.Now;
                    double Hyper_time = (Hyper_end - Hyper_start).TotalMilliseconds;
                    Console.WriteLine(final.Count);

                    Hyper_start = DateTime.Now;
                    Tuple<double, double> results = icm.InfluenceSpread(graph, final, 20000, 0.7);
                    Hyper_end = DateTime.Now;
                    FileStream outfile = new FileStream(filepath+"_9n.txt", FileMode.Append);
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
