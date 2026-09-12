package org.example.neutralbench;
import android.app.Activity;
import android.os.Bundle;
import android.graphics.Canvas;
import android.graphics.Color;
import android.graphics.Paint;
import android.view.View;
import android.view.Choreographer;
import java.util.ArrayList;
import java.util.concurrent.CountDownLatch;

public class MainActivity extends Activity {
 public Scene scene;
 @Override public void onCreate(Bundle b) { super.onCreate(b); scene=new Scene(); setContentView(scene); }
 public class Scene extends View implements Choreographer.FrameCallback {
  Paint p=new Paint(); int frame=0; boolean running=false; long first,last; CountDownLatch done;
  public ArrayList<Long> intervals=new ArrayList<>();
  Scene(){super(MainActivity.this);}
  public void begin(CountDownLatch latch){done=latch;frame=0;first=last=0;intervals.clear();running=true;invalidate();}
  @Override public void doFrame(long nanos){if(running) invalidate();}
  @Override public void onDraw(Canvas c){
   c.drawColor(Color.rgb(18,22,30));
   for(int i=0;i<120;i++){p.setColor(Color.rgb((i*41)%256,(i*67)%256,(i*97)%256));int x=(i*83+frame*7)%960,y=(i*127+frame*3)%1600;c.drawRect(x,y,x+80,y+50,p);}
   p.setColor(Color.WHITE);p.setTextSize(32);c.drawText("Neutral deterministic benchmark",24,48,p);
   if(running){long now=System.nanoTime();if(frame==0)first=now;else intervals.add(now-last);last=now;frame++;
    if(frame>=30){running=false;done.countDown();}else Choreographer.getInstance().postFrameCallback(this);
   }
  }
  public long duration(){return last-first;}
 }
}
