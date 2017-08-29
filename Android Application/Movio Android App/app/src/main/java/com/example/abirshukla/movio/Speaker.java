package com.example.abirshukla.movio;

import android.app.Activity;
import android.content.DialogInterface;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.speech.tts.TextToSpeech;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;
import java.util.Locale;


public class Speaker extends Activity implements DialogInterface.OnClickListener, TextToSpeech.OnInitListener, View.OnClickListener {
    //TTS object
    private TextToSpeech myTTS;
    private TextToSpeech myTTSA;
    //status check code
    private int MY_DATA_CHECK_CODE = 0;
    TextView said;
    Intent a;
    String url;
    //create the Activity
    public void onCreate(Bundle savedInstanceState) {

        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_speaker);
        //listen for clicks
        said = (TextView) findViewById(R.id.enter);

        //check for TTS data
        Intent checkTTSIntent = new Intent();
        checkTTSIntent.setAction(TextToSpeech.Engine.ACTION_CHECK_TTS_DATA);
        startActivityForResult(checkTTSIntent, MY_DATA_CHECK_CODE);
        Bundle wor = getIntent().getExtras();
        String res = wor.getString("res");
        System.out.println("Res: " + res);

        if (res.contains("http://")) {
            movioSpeak("Here is an I M D B Page on the Movie");
            res = res.replace("http://rss.","http://www.");
            a = new Intent(this, Home.class);
            a.putExtra("say", "");
            startActivity(a);
            Intent intent= new Intent(Intent.ACTION_VIEW,Uri.parse(res));
            startActivity(intent);
            return;
        }
        said.setText(res);

        movioSpeak(res);
        if (res.equals("Here are some Sample Voice Commands")) {
            a = new Intent(this, Sample.class);

            startActivity(a);
        }
        else {
            if (res.equals("Error Occured Try Again Later")) {
                DataForUser.errorCount++;
            }
            a = new Intent(this, Home.class);
            a.putExtra("say", res);
            startActivity(a);
        }
    }
    public void movioSpeak(final String speech) {
        Intent checkTTSIntentA = new Intent();
        checkTTSIntentA.setAction(TextToSpeech.Engine.ACTION_CHECK_TTS_DATA);
        startActivityForResult(checkTTSIntentA, MY_DATA_CHECK_CODE);
        myTTSA = new TextToSpeech(getApplicationContext(), new TextToSpeech.OnInitListener() {
            @Override
            public void onInit(int status) {
                if(status != TextToSpeech.ERROR) {
                    myTTSA.setLanguage(Locale.UK);
                    myTTSA.speak(speech, TextToSpeech.QUEUE_FLUSH, null);


                }
            }
        });
    }
    //respond to button clicks

    //speak the user text
    private void speakWords(String speech) {

        //speak straight away
        myTTS.speak(speech, TextToSpeech.QUEUE_FLUSH, null);
    }

    //act on result of TTS data check
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {

        if (requestCode == MY_DATA_CHECK_CODE) {
            if (resultCode == TextToSpeech.Engine.CHECK_VOICE_DATA_PASS) {
                //the user has the necessary data - create the TTS
                myTTS = new TextToSpeech(this, this);
            }
            else {
                //no data - install it now
                Intent installTTSIntent = new Intent();
                installTTSIntent.setAction(TextToSpeech.Engine.ACTION_INSTALL_TTS_DATA);
                startActivity(installTTSIntent);
            }
        }
    }

    //setup TTS
    public void onInit(int initStatus) {

        //check for successful instantiation
        if (initStatus == TextToSpeech.SUCCESS) {
            if(myTTS.isLanguageAvailable(Locale.US)==TextToSpeech.LANG_AVAILABLE)
                myTTS.setLanguage(Locale.US);
        }
        else if (initStatus == TextToSpeech.ERROR) {
            Toast.makeText(this, "Sorry! Text To Speech failed...", Toast.LENGTH_LONG).show();
        }
    }

    @Override
    public void onClick(DialogInterface dialog, int which) {

    }





    @Override
    protected void onDestroy() {
        myTTSA.stop();
        myTTSA.shutdown();
        super.onDestroy();
    }

    @Override
    public void onClick(View view) {

    }
}