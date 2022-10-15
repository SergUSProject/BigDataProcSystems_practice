lazy val commonSettings = Seq(
  name := "Spark_test",
  version := "1.0",
  scalaVersion := "2.12.14",
  libraryDependencies += "org.apache.spark" %%  "spark-core" % "3.1.2",
  libraryDependencies += "org.apache.spark" %%  "spark-sql" % "3.1.2",
  libraryDependencies += "org.apache.spark" %% "spark-mllib" % "3.1.2"
)

lazy val root = (project in file(".")).
  settings(commonSettings: _*).
  enablePlugins(AssemblyPlugin)

assemblyMergeStrategy in assembly := {
  case PathList("META-INF", xs@_*) => MergeStrategy.discard
  case x => MergeStrategy.first
}

assemblyJarName in assembly := "Spark_test.jar"






