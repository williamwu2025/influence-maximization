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
            List<int> seeds = new List<int>();
            for (int i = 0; i < 100; i++)
            {
                seeds.Add(int.Parse(initial.ReadLine()));
             }
            double alpha = 0.6; // Step of c of searching the best discount in th Unified Discount Algorithm
            while (alpha <= 1.0)
            {
                Bipartite bg = new Bipartite(filepath, alpha, graph.numV);
                int b = 10;
                while (b <= 50)
                // Build a random hyper graph with mH random hyper edges.
                {
                    DateTime Hyper_start = DateTime.Now;
                    ICModel icm = new ICModel(alpha);
                    Tuple<List<int>, double>choose = bg.Greedy(b, seeds);
                    DateTime Hyper_end = DateTime.Now;
                    double Hyper_time = (Hyper_end - Hyper_start).TotalMilliseconds;
                    FileStream outfile = new FileStream(filepath+"_2o.txt", FileMode.Append);
                    StreamWriter writer = new StreamWriter(outfile);
                    writer.Write("Choose time:\t" + Hyper_time + "\t");

                    Hyper_start = DateTime.Now;
                    Tuple<double, double> results = icm.InfluenceSpread(graph, choose.Item1, 100);
                    Hyper_end = DateTime.Now;
                    Hyper_time = (Hyper_end - Hyper_start).TotalMilliseconds;
                    string mem = Convert.ToString(Process.GetCurrentProcess().WorkingSet64/8/1024/1024);
                    writer.Write("Propagation time:\t" + Hyper_time + "\t");
                    writer.Write("a:" + alpha + "\tb:" + b + "\tave:" + results.Item1 + "\tstd:" + results.Item2+"\tmemory:"+mem+"\n");
                    writer.Flush();
                    writer.Close();
                    b += 10;
                }
                alpha += 0.2;
            }
        }
    }
}
