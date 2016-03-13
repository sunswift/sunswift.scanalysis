<!--
speed=1000;
len=40;
tid = 0;
num=0;
clockA = new Array();
timeA = new Array();
formatA = new Array();
dd = new Date();
var d,x;
var makespace = "&#160;";

function doDate(x)
{
  for (i=0;i<num;i++) {
    dt = new Date();
  
    if (timeA[i] != 0) {
      v1 = Math.round(( timeA[i] - dt )/1000) ;
      if (v1 < 0)
        clockA[i].date.value = "**BANG!**";
      if (formatA[i] == 1)
        clockA[i].date.value = v1;
      else if (formatA[i] ==2) {
        sec = v1%60;
		v1 = Math.floor( v1/60);
		min = v1 %60 ;
		hour = Math.floor(v1 / 60);
	if (sec < 10 ) sec = "0"+sec;
	if (min < 10 ) min = "0"+min;
        clockA[i].date.value = hour+"h "+min+"m "+sec+"s";
    } else if (formatA[i] ==3) {
        sec = v1%60;
		v1 = Math.floor( v1/60);
		min = v1 %60 ;
		v1 = Math.floor(v1 / 60);
		hour = v1 %24 ;
		day = Math.floor(v1 / 24);
	if (sec < 10 ) sec = "0"+sec;
	if (min < 10 ) min = "0"+min;
	if (hour < 10 ) hour = "0"+hour;
        clockA[i].date.value = day+"d "+hour+"h "+min+"m "+sec+"s";
    }else if (formatA[i] == 4 ) {
        sec = v1%60;
		v1 = Math.floor( v1/60);
		min = v1 %60 ;
		v1 = Math.floor(v1 / 60);
		hour = v1 %24 ;
		day = Math.floor(v1 / 24);
        document.getElementById("timer").innerHTML = day+makespace+(day==1?"day, ":"days, ")+hour+makespace+(hour==1?"hour, ":"hours, ")+min+makespace+(min==1?"min, ":"mins, ")+sec+makespace+(sec==1?"sec ":"secs ")
        }
      else
        document.getElementById("timer").innerHTML = "Invalid date format specification entered";
      }
    else
      document.getElementById("timer").innerHTML = "Countdown until when?";
    }

  tid=window.setTimeout("doDate()",speed);
}

function start(d,x,format) {
  clockA[num] = x
  timeA[num] = new Date(d);
  formatA[num] = format;
  if (num == 0)  
    tid=window.setTimeout("doDate()",speed);
  num++;
}

function CountdownLong(t,format,len)
{
  start(t,'',format);
}

function Countdown2001seconds()
{
  CountdownLong("January 01, 2001 00:00:00",1,8);
}

function Countdown2001()
{
  //CountdownLong("January 01, 2000 00:00:00",3,20);
  CountdownLong("January 01, 2001 00:00:00",4,20);
}

function Countdown(t)
{
  CountdownLong(t,4,30);
}
// end-->