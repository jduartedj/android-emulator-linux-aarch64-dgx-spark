package org.example.neutralbench;
import android.app.Instrumentation;
import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.database.Cursor;
import android.database.sqlite.SQLiteDatabase;
import android.database.sqlite.SQLiteStatement;
import java.io.*;
import java.util.*;
import java.util.concurrent.*;
import org.json.*;

public class BenchInstrumentation extends Instrumentation {
 Bundle args; ExecutorService pool; PrintWriter out; File root; byte[] payload=new byte[1024*1024];
 public void onCreate(Bundle a){args=a;start();}
 static int compute(){int x=0x12345678;for(int i=0;i<2000000;i++){x^=x<<13;x^=x>>>17;x^=x<<5;x+=0x9e3779b9;}return x;}
 static void check(boolean ok,String why){if(!ok)throw new AssertionError(why);}
 public void onStart(){Bundle result=new Bundle();try{
  root=getTargetContext().getFilesDir();pool=Executors.newFixedThreadPool(4);
  for(int i=0;i<payload.length;i++)payload[i]=(byte)(i*31+7);
  String batch=args.getString("batch","0");check(batch.matches("[0-9]+"),"batch");
  int warm="true".equals(args.getString("smoke"))?1:5,n="true".equals(args.getString("smoke"))?1:30;
  out=new PrintWriter(new File(root,"batch-"+batch+".jsonl"),"UTF-8");
  for(String name:new String[]{"cpu1","cpu4","sqlite","file_sync","ui30"}){
   MainActivity activity=null;
   if(name.equals("ui30")){Intent in=new Intent(getTargetContext(),MainActivity.class).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);activity=(MainActivity)startActivitySync(in);waitForIdleSync();}
   for(int i=-warm;i<n;i++){
    JSONObject row=new JSONObject();row.put("metric",name);row.put("batch",Integer.parseInt(batch));row.put("sample",i<0?i+warm:i);row.put("phase",i<0?"warmup":"measure");row.put("utc_ms",System.currentTimeMillis());
    long start=0,elapsed=0;String checksum="";
    if(name.equals("cpu1")){start=System.nanoTime();int x=compute();elapsed=System.nanoTime()-start;check(x==-80449474,"cpu1 checksum");checksum="-80449474";}
    if(name.equals("cpu4")){start=System.nanoTime();List<Future<Integer>> fs=new ArrayList<>();for(int t=0;t<4;t++)fs.add(pool.submit(()->compute()));long sum=0;for(Future<Integer> f:fs){int x=f.get();check(x==-80449474,"cpu4 checksum");sum+=x;}elapsed=System.nanoTime()-start;checksum=Long.toString(sum);}
    if(name.equals("sqlite")){
     File f=new File(root,"bench.db");SQLiteDatabase.deleteDatabase(f);SQLiteDatabase db=SQLiteDatabase.openOrCreateDatabase(f,null);
     Cursor mode=db.rawQuery("PRAGMA journal_mode=DELETE",null);check(mode.moveToFirst()&&mode.getString(0).equalsIgnoreCase("delete"),"journal mode");mode.close();db.execSQL("PRAGMA synchronous=FULL");Cursor sync=db.rawQuery("PRAGMA synchronous",null);check(sync.moveToFirst()&&sync.getInt(0)==2,"synchronous FULL");sync.close();db.execSQL("CREATE TABLE t(id INTEGER PRIMARY KEY,v TEXT)");SQLiteStatement stmt=db.compileStatement("INSERT INTO t VALUES (?,?)");
     start=System.nanoTime();db.beginTransaction();for(int k=0;k<512;k++){stmt.bindLong(1,k);stmt.bindString(2,"row-"+k);stmt.executeInsert();}db.setTransactionSuccessful();db.endTransaction();
     long sum=0;int count=0;Cursor cur=db.rawQuery("SELECT id,v FROM t ORDER BY id",null);while(cur.moveToNext()){int k=cur.getInt(0);check(cur.getString(1).equals("row-"+k),"sqlite value");sum+=k;count++;}cur.close();elapsed=System.nanoTime()-start;
     check(count==512&&sum==130816,"sqlite checksum");checksum=count+":"+sum;stmt.close();db.close();SQLiteDatabase.deleteDatabase(f);
    }
    if(name.equals("file_sync")){
     File f=new File(root,"bench.bin");byte[] buf=new byte[65536];start=System.nanoTime();FileOutputStream w=new FileOutputStream(f);w.write(payload);w.getFD().sync();w.close();FileInputStream r=new FileInputStream(f);long sum=0;int total=0,len;while((len=r.read(buf))!=-1){for(int k=0;k<len;k++)sum+=buf[k]&255;total+=len;}r.close();elapsed=System.nanoTime()-start;
     check(total==1048576&&sum==133693440L,"file checksum");checksum=total+":"+sum;check(f.delete(),"delete own IO file");
    }
    if(name.equals("ui30")){
     MainActivity a=activity;CountDownLatch done=new CountDownLatch(1);runOnMainSync(()->a.scene.begin(done));check(done.await(15,TimeUnit.SECONDS),"UI timeout");elapsed=a.scene.duration();check(a.scene.intervals.size()==29,"UI draw count");JSONArray intervals=new JSONArray();int slow=0;for(long v:a.scene.intervals){intervals.put(v);if(v>25000000)slow++;}row.put("frame_intervals_ns",intervals);row.put("frames_over_25ms",slow);checksum="30-draws";
    }
    row.put("duration_ns",elapsed);row.put("checksum",checksum);row.put("correct",true);out.println(row.toString());out.flush();
   }
   if(activity!=null){MainActivity a=activity;runOnMainSync(()->a.finish());waitForIdleSync();}
  }
  result.putString("result","PASS");finish(Activity.RESULT_OK,result);
 }catch(Throwable e){result.putString("error",e.toString());finish(Activity.RESULT_CANCELED,result);}finally{if(out!=null)out.close();if(pool!=null)pool.shutdown();}}
}
