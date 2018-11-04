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
            StreamReader initial = new StreamReader(filepath+"_ini1000.txt");
            StreamReader nodetype = new StreamReader(filepath + "_typeo.txt");
            List<int> type = new List<int>();
            for (int i = 0; i < graph.numV; i++)
            {
                int flag = int.Parse(nodetype.ReadLine());
                if (flag == 0) { type.Add(0); }
                else if (flag == 1) { type.Add(2); }
                else { type.Add(1); }
            }
            List<int> initNodes = new List<int>();
            for (int i = 0; i < 1000; i++) { initNodes.Add(int.Parse(initial.ReadLine()));}
            int mh = 0;
            if (filepath.Contains("Wiki")){mh = 250000;}
            else if (filepath.Contains("CA")) { mh = 2000000; }
            else if (filepath.Contains("dblp")) { mh = 20000000; }
            else { mh = 40000000; }
            double alpha = 1.0; // Step of c of searching the best discount in th Unified Discount Algorithm
            while (alpha <= 1.0)
            {
                Bipartite bg = new Bipartite(filepath, alpha, graph.numV);
                int b = 10;
                while (b <= 50)
                // Build a random hyper graph with mH random hyper edges.
                {
                    DateTime Hyper_start = DateTime.Now;
                    ICModel icm = new ICModel(alpha);
                    int count = Convert.ToInt16(1.5 * Convert.ToDouble(b));
                    List<int> degrees = new List<int>();
                    for (int i = 0; i < 1000; i++) { degrees.Add(graph.adj[initNodes[i]].Count); }
                    List<int> seedNodes = new List<int>();
                    while (count > 0)
                    {
                        int flag = 0;
                        for (int i = 1; i < 1000; i++) {if (degrees[i] > degrees[flag]) flag = i;}
                        seedNodes.Add(initNodes[flag]);
                        degrees[flag] = -1;
                        count--;
                    }
                    CoordinateDescent cd = new CoordinateDescent(graph, bg, initNodes, seedNodes, 1/1.5, type, 50, alpha, mh);
                    List<double> allocation = cd.IterativeMinimize();
                    DateTime Hyper_end = DateTime.Now;
                    double Hyper_time = (Hyper_end - Hyper_start).TotalMilliseconds;
                    FileStream outfile = new FileStream(filepath+"_3l.txt", FileMode.Append);
                    StreamWriter writer = new StreamWriter(outfile);
                    writer.Write("Choose time:" + Hyper_time + "\t");

                    List<double> prob = new List<double>();
                    for (int i = 0; i < initNodes.Count; i++){prob.Add(cd.SeedProb(initNodes[i], allocation[initNodes[i]]));}

                    Hyper_start = DateTime.Now;
                    Tuple<double, double> results = icm.InfluenceSpread(graph, initNodes, prob, 20000);
                    Hyper_end = DateTime.Now;
                    string mem = Convert.ToString(Process.GetCurrentProcess().WorkingSet64/8/1024/1024);
                    Hyper_time = (Hyper_end - Hyper_start).TotalMilliseconds;
                    writer.Write("Propagation time:" + Hyper_time + "\t");
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
