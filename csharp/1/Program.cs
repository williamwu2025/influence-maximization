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
        public static string filepath = "/home/sjtuiiot/wcy/im/com-dblp.ungraph";
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
            List<int> seeds = new List<int>();
            for (int i = 0; i < 100; i++) { seeds.Add(int.Parse(initial.ReadLine()));}
            int mh = 0;
            if (filepath.Contains("Wiki")){mh = 250000;}
            else if (filepath.Contains("CA")) { mh = 2000000; }
            else if (filepath.Contains("dblp")) { mh = 20000000; }
            else { mh = 40000000; }
            double alpha = 0.6; // Step of c of searching the best discount in th Unified Discount Algorithm
            while (alpha <= 0.6)
            {
                int b1 = 2;
                while (b1 <= 2)
                // Build a random hyper graph with mH random hyper edges.
                {
                    int b2 = b1 * 4;
                    DateTime Hyper_start = DateTime.Now;
                    ICModel icm = new ICModel(alpha);
                    List<int> seed1 = new List<int>();
                    List<int> seed2 = new List<int>();
                    Random random = new Random();
                    for (int i = 0; i < b1; i++)
                    { 
                        int pos = random.Next(0, 100);
                        while (seed1.Contains(seeds[pos]))
                        { pos = random.Next(0, 100); }
                        seed1.Add(seeds[pos]);
                    }
                    Console.WriteLine(seed1.Count);
                    List<int> neighbor = new List<int>();
                    foreach (int i in seed1)
                    {
                        foreach (Node j in graph.adj[i])
                        {
                            if ((!seeds.Contains(j.id)) && !neighbor.Contains(j.id))
                            {neighbor.Add(j.id);}
                        }
                    }
                    if (neighbor.Count <= b2)
                    {
                        foreach (int u in neighbor) seed2.Add(u);
                    }
                    else
                    {
                        for (int i = 0; i < b2; i++)
                        {
                            int pos = random.Next(0, neighbor.Count);
                            while (seed2.Contains(neighbor[pos]))
                            { pos = random.Next(0, neighbor.Count);}
                            seed2.Add(neighbor[pos]);
                        }
                    }
                    Console.WriteLine(seed2.Count);
                    DateTime Hyper_end = DateTime.Now;
                    double Hyper_time = (Hyper_end - Hyper_start).TotalMilliseconds;
                    FileStream outfile = new FileStream(filepath+"_1o.txt", FileMode.Append);
                    StreamWriter writer = new StreamWriter(outfile);
                    writer.Write("Choose time:" + Hyper_time + "\t");

                    Hyper_start = DateTime.Now;
                    Tuple<double, double> results = icm.InfluenceSpread(graph, seed2, 20000);
                    Hyper_end = DateTime.Now;
                    Hyper_time = (Hyper_end - Hyper_start).TotalMilliseconds;
                    writer.Write("Propagation time:" + Hyper_time + "\t");
                    string mem = Convert.ToString(Process.GetCurrentProcess().WorkingSet64/8/1024/1024);
                    writer.Write("a:" + alpha + "\tb:" + (b1+b2) + "\tave:" + results.Item1 + "\tstd:" + results.Item2+"\tmemory:"+mem+"\n");
                    writer.Flush();
                    writer.Close();
                    b1 += 2;
                }
                alpha += 0.2;
            }
        }
    }
}
