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
            double alpha = 0.6; // Step of c of searching the best discount in th Unified Discount Algorithm
            while (alpha <= 0.6)
            {
                int b = 10;
                while (b <= 10)
                // Build a random hyper graph with mH random hyper edges.
                {
                    StreamReader initial = new StreamReader(filepath + Convert.ToString(b) + ".txt");
                    List<int> seed = new List<int>();
                    while (true)
                    {
                        string line = initial.ReadLine();
                        if (line.StartsWith("t")) break;
                        seed.Add(int.Parse(line));
                    }
                    ICModel icm = new ICModel(alpha);
                    for (int s = 0; s < seed.Count; s = s + 1)
                    {
                        int e = Math.Min(s + Convert.ToInt32((Convert.ToDouble(b)*0.8)), seed.Count);
                        List<int> final = new List<int>();
                        for (int node = s; node < e; node = node + 1) { final.Add(seed[node]); }
                        DateTime Hyper_start = DateTime.Now;
                        Tuple<double, double> results = icm.InfluenceSpread(graph, final, 200, 1.0);
                        DateTime Hyper_end = DateTime.Now;
                        double Hyper_time = (Hyper_end - Hyper_start).TotalMilliseconds;
                        FileStream outfile = new FileStream(filepath + "_10n.txt", FileMode.Append);
                        StreamWriter writer = new StreamWriter(outfile);
                        string mem = Convert.ToString(Process.GetCurrentProcess().WorkingSet64 / 8 / 1024 / 1024);
                        writer.Write("Propagation time:" + Hyper_time + "\t");
                        writer.Write("a:" + alpha + "\tb:" + b + "\tave:" + results.Item1 + "\tstd:" + results.Item2 + "\tmemory:" + mem + "offset"+Convert.ToString(s)+"\n");
                        writer.Flush();
                        writer.Close();
                    }
                    b += 10;
                }
                alpha += 0.2;
            }
        }
    }
}
