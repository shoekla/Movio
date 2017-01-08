package com.example.abirshukla.movio;

import android.app.ProgressDialog;
import android.content.ActivityNotFoundException;
import android.content.Intent;
import android.os.Bundle;
import android.speech.RecognizerIntent;
import android.support.v7.app.AppCompatActivity;
import android.view.KeyEvent;
import android.view.View;
import android.widget.TextView;
import android.widget.Toast;

import com.koushikdutta.async.future.FutureCallback;
import com.koushikdutta.ion.Ion;

import java.util.ArrayList;
import java.util.Locale;
import java.util.Random;

public class Home extends AppCompatActivity {
    private final int REQ_CODE_SPEECH_INPUT = 100;
    TextView textView;
    ProgressDialog progress;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_home);
        Bundle wor = getIntent().getExtras();
        String say = wor.getString("say");
        textView = (TextView) findViewById(R.id.textView);
        textView.setText(say);
        progress = new ProgressDialog(this);
        progress.setMessage("Processing Command...");
        progress.setProgressStyle(android.R.style.Widget_ProgressBar_Small);
        if (DataForUser.errorCount == 3) {
            progress.setMessage("Fixing Errors...");
            progress.show();
            getHTML("http://abirshukla.pythonanywhere.com/movio/restoreUser/"+DataForUser.getUser());
            progress.hide();
            progress.dismiss();
            progress.setMessage("Processing Command...");

        }
        System.out.println("Info: userName home: "+DataForUser.getUser());
        if (DataForUser.firstTime == 1) {
            DataForUser.firstTime = 0;
        }
        else {
            TextView hint = (TextView) findViewById(R.id.textView2);
            String hintArr[] = {"Say 'help' for Sample Commands", "Example: 'I liked Star Wars'", "Example: 'I did not like Star Wars'", "Example: 'Will I like Star Wars'", "Example: 'Info on 'Star Wars'"};
            Random random = new Random();
            hint.setText(hintArr[random.nextInt(5)]);
        }
    }
    public void getVoice(View view) {
        promptSpeechInput();
    }
    private void promptSpeechInput() {
        String speech_prompt = "Speak Command";
        Intent intent = new Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH);
        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM);
        intent.putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault());
        intent.putExtra(RecognizerIntent.EXTRA_PROMPT,
                speech_prompt);
        try {
            startActivityForResult(intent, REQ_CODE_SPEECH_INPUT);

        } catch (ActivityNotFoundException a) {
            Toast.makeText(getApplicationContext(), "Speech Not Supported",
                    Toast.LENGTH_SHORT).show();
            return;
        }
    }

    @Override
    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        String res = "";
        super.onActivityResult(requestCode, resultCode, data);

        switch (requestCode) {
            case REQ_CODE_SPEECH_INPUT: {
                if (resultCode == RESULT_OK && null != data) {

                    ArrayList<String> result = data
                            .getStringArrayListExtra(RecognizerIntent.EXTRA_RESULTS);
                    res = result.get(0);
                }
                break;
            }

        }
        //Intent speak = new Intent(MainActivity.this, speaker.class);
        //speak.putExtra("res",res);
        //startActivity(speak);
        res = res.toLowerCase();
        if (res.contains("log out")) {
            DataForUser.setUser("");
            DataForUser.logOut = 1;
            Intent m = new Intent(Home.this,MainActivity.class);
            startActivity(m);
            return;
        }
        if (res.equals("help")) {
            Intent speak = new Intent(Home.this,Speaker.class);
            speak.putExtra("res","Here are some Sample Voice Commands");
            startActivity(speak);
            return;
        }
        textView.setText(res);
        progress.show();
        String url = "http://abirshukla.pythonanywhere.com/movio/message/"+DataForUser.getUser()+"/"+res;
        getHTML(url);
    }
    public void getHTML(final String url) {
        if (url.contains("restoreUser")) {
            System.out.println("Begin HTML");
            System.out.println("Final Url: " + url);
            final String[] d = new String[1];
            Ion.with(getApplicationContext())
                    .load(url)
                    .asString()
                    .setCallback(new FutureCallback<String>() {
                        @Override
                        public void onCompleted(Exception e, String result) {
                            if (result.equals("All Good!")) {
                                DataForUser.errorCount = 0;
                            }
                        }
                    });
            return;
        }
        System.out.println("Begin HTML");
        System.out.println("Final Url: " + url);
        final String[] d = new String[1];
        Ion.with(getApplicationContext())
                .load(url)
                .asString()
                .setCallback(new FutureCallback<String>() {
                    @Override
                    public void onCompleted(Exception e, String result) {
                        if (result.contains("<!DOCTYPE")) {
                            Intent speak = new Intent(Home.this,Speaker.class);
                            speak.putExtra("res","Error Occured Try Again Later");
                            progress.hide();
                            progress.dismiss();
                            startActivity(speak);
                        }
                        else {
                            Intent speak = new Intent(Home.this, Speaker.class);
                            speak.putExtra("res", result);
                            progress.hide();
                            progress.dismiss();
                            startActivity(speak);
                        }
                    }
                });
    }
    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event)  {
        if (Integer.parseInt(android.os.Build.VERSION.SDK) > 5
                && keyCode == KeyEvent.KEYCODE_BACK
                && event.getRepeatCount() == 0) {
            onBackPressed();
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }


    @Override
    public void onBackPressed() {
        textView.setText("");
    }
}
