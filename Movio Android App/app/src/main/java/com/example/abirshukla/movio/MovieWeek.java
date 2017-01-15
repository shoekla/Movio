package com.example.abirshukla.movio;

import android.app.ProgressDialog;
import android.content.Intent;
import android.os.Bundle;
import android.support.v7.app.AppCompatActivity;
import android.view.View;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.ListView;
import android.widget.Toast;

import com.koushikdutta.async.future.FutureCallback;
import com.koushikdutta.ion.Ion;

public class MovieWeek extends AppCompatActivity {
    ListView listView;
    ProgressDialog progress;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_movie_week);
        Bundle dataUser = getIntent().getExtras();
        DataForUser.setUser(dataUser.getString("user"));
        Toast.makeText(getApplicationContext(),DataForUser.getUser()+" Logged In",
                Toast.LENGTH_SHORT).show();

        progress = new ProgressDialog(this);
        progress.setMessage("Getting Movies You May Like...");
        progress.setProgressStyle(android.R.style.Widget_ProgressBar_Small);
        progress.show();
        getMovies();

    }

    public void getMovies() {
       String url = "http://abirshukla.pythonanywhere.com/soonMovie/"+DataForUser.getUser();
        System.out.println("Final Url: " + url);
        final String[] d = new String[1];
        Ion.with(getApplicationContext())
                .load(url)
                .asString()
                .setCallback(new FutureCallback<String>() {
                    @Override
                    public void onCompleted(Exception e, String result) {
                        String StringArray[] = result.split(",");
                        final String sarr[] = new String[StringArray.length];

                        for (int i = 0; i < StringArray.length;i++) {
                            sarr[i] = StringArray[i].substring(1,StringArray[i].length()-1);
                        }
                        progress.hide();
                        progress.dismiss();
                        ArrayAdapter adapter = new ArrayAdapter<String>(MovieWeek.this,R.layout.listview,sarr);
                        ListView listView = (ListView) findViewById(R.id.mobile_list);
                        listView.setAdapter(adapter);
                        listView.setOnItemClickListener(new AdapterView.OnItemClickListener() {
                            @Override
                            public void onItemClick(AdapterView<?> parent, View view, int position, long id) {

                                // selected item
                                getMovieInfo(sarr[position]);
                                Toast toast = Toast.makeText(getApplicationContext(), "Opening "+sarr[position]+ " on Web", Toast.LENGTH_SHORT);
                                toast.show();
                            }
                        });
                    }
                });
    }

    public void getMovieInfo(String movieName) {
        String url = "http://abirshukla.pythonanywhere.com/movio/message/info on "+movieName;
        final String[] d = new String[1];
        Ion.with(getApplicationContext())
                .load(url)
                .asString()
                .setCallback(new FutureCallback<String>() {
                    @Override
                    public void onCompleted(Exception e, String result) {
                        if (result.contains("<!DOCTYPE")) {
                            Toast toast = Toast.makeText(getApplicationContext(), "Error Occured", Toast.LENGTH_SHORT);
                            return;
                        }
                        else {
                            Intent openWeb = new Intent(MovieWeek.this, Web.class);
                            openWeb.putExtra("url", result);
                            startActivity(openWeb);
                        }
                    }
                });
    }



}
