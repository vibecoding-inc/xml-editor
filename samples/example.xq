(: Example XQuery :)
xquery version "1.0";
<Result_Example_XQuery>{

for $s in /staffinfo/job/title

return
  <JobTitle> {$s/text()} </JobTitle>,
let $k := count(/staffinfo/job/title)
return
  <CountJobTitle> {$k} </CountJobTitle>

}</Result_Example_XQuery>
