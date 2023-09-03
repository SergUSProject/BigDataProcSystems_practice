name := "WordCountApp"

version := "0.1"

scalaVersion := "2.13.1"

//unmanagedBase := file("/usr/lib/hadoop/share/hadoop/client")

unmanagedJars in Compile ++= {
  val hadoopClient = file("/usr/lib/hadoop/share/hadoop/client")
  val hadoop = file("/usr/lib/hadoop/share/hadoop/common")
  ((libs +++ libs2) ** "*.jar").classpath
}

// libraryDependencies += "org.apache.hadoop" % "hadoop-client" % "3.1.2"

// libraryDependencies += "org.apache.hadoop" % "hadoop-client" % "3.1.2" from "file:///usr/lib/hadoop/share/hadoop/client/hadoop-client-api-3.1.2.jar"