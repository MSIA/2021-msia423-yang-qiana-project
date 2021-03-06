# Find Like-Minded Souls: A Reciprocal Recommendation System

Qiana Yang, with QA contributions from Louis-Charles Généreux

Northwestern University MS in Analytics Course Project: Analytics Value Chain

## Project Charter

Perhaps you are an MSiA student new to the program, hoping to find compatible partners for group projects. Or perhaps you are a singleton in search of a perfect match without resorting to traditional dating apps. Whether you're in need of a new friend or looking to form deep bonds with a like-minded person, a reciprocal recommendation system can give you a little nudge to build a meaningful connection with the right person at the right time. 

**Vision**

This app aims to help users find other users with similar personality traits. If deployed in professional settings, the app can also help users make informed decisions about who to team up with on a business project.

**Mission**

Each app user will fill out Cattell's 16 personality survey to the best of their ability. Based on the survey results, the recommender will map the user to a vector in an embedding space with factor and clustering analyses. The recommender will then output a list of new user profiles based on their proximity to the first user profile.

Although the app will ultimately rely on real-time data from its user base, it will use a static dataset for the initial launch. The dataset in question consists of approximately 50000 rows of anonymized user survey results published on [openpsychometrics.org](openpsychometrics.org) (download [here](http://openpsychometrics.org/_rawdata/16PF.zip)). An interactive version of the survey can be found at [openpsychometrics.org/tests/16PF.php](https://openpsychometrics.org/tests/16PF.php).

**Success criteria**

*Machine learning performance metric:* 

Because the recommendation system uses unsupervised learning algorithms, we will rely on the silhoutte score and reduction in SSE to select the optimal number of clusters, and use the Kaiser criteria for dimensionality reduction and factor analysis. There's no hard success threshold we can aim for &ndash, but I hope to retain features that capture around 95% of the variation in the data as I perform factor analysis.

Once the app is launched, we can then calculate the precision, recall, AUC, and F1 score of our recommendation engine based on dynamic user feedback. Tinder's current algorithm has an astonishing AUC of 90% and F1 of 85% &ndash; these are the numbers I'll be aiming for. 

*Business metric:*

We can measure the business value of the app based on user acquisition rates, churn rates, user engagement metrics (e.g. average session duration and total time on app), and of course, the number of successful matches made based on user feedback (e.g. number of successful matches divided by total time on app per user).


## Directory structure 

```
├── README.md                         <- You are here
├── app
│   ├── static/                       <- static CSS files
│   ├── templates/                    <- templated HTML files
│
├── config                            <- Directory for configuration files 
│   ├── flaskconfig.py                <- Configurations for Flask API 
│
├── data                              <- Folder that contains data used or generated. Not tracked by git. 
│
├── deliverables/                     <- App presentation slides.
│   ├── MSiA_presentation.pdf         <- Final presentation slides.
│
├── src/                              <- Source files for the app 
│   ├── create_db.py                  <- Python objects to create database instance, generate schema, and manipulate records for the app
│   ├── forms.py                      <- Flask forms for the registration and login pages
│   ├── ingest.py                     <- Python class to acquire raw data and download/upload objects to s3
│   ├── modeling.py                   <- Python class for the offline modeling process
│
├── test/                             <- Folder for running model tests
│   ├── test_modeling.py                <- Unit test for the offline modeling process
│
├── app.py                            <- Flask wrapper for running the model 
├── run.py                            <- Simplifies the execution of the src scripts 
├── run_modeling_pipeline.py          <- Runs the offline modeling process in separate steps  
├── requirements.txt                  <- Python package dependencies 
├── run.py                            <- Simplifies the execution of one or more of the src scripts 
├── Dockerfile                        <- File required to run the entire pipeline in docker
├── Makefile                          <- File required to execute the docker commands as outlined in the section below
```


## User Manual

#### 1. Set Configurations

You will need to set a number of environment variables to run the app. First, you will need to execute the following to connect to an s3 bucket on AWS:
```shell script
export AWS_ACCESS_KEY_ID=<aws_access_key_id>
export AWS_SECRET_ACCESS_KEY=<aws_secret_access_key>
export S3_BUCKET=<s3_bucket_name>
```
Then, either set the following environment variables to connect to an RDS database:
```shell script
export MYSQL_USER=<mysql_user>
export MYSQL_PASSWORD=<mysql_password>
export MYSQL_HOST=<mysql_host>
export MYSQL_PORT=<mysql_port>
export DATABASE_NAME=<database_name>
```
Or alternatively, set the following variable to connect to a custom database of your choice:
```shell script
export SQLALCHEMY_DATABASE_URI=<custom_database_engine_string>
```
*Even though you can set up a local sqlite instance for development and debugging, you will need a mysql database for final app deployment due to some syntactical constraints. More on this in the sections below.*

During app setup, we will upload a series of artifacts to the s3 bucket. Those include a raw csv file comprising the seed data for our model and app, a data codebook for the csv file, a factor analysis model for feature generation, and a cluster analysis model for efficient SQL queries. The default s3 file paths for these 4 objects are in the `config/flaskconfig.py` file. However, you may override the defualt settings with relevant environment variables as follows:
```shell script
export CODEBOOK_PATH=<codebook_path>
export DATA_PATH=<data_path>
export FA_PATH=<factor_analysis_model_path>
export CA_PATH=<clustering_model_path>
```

#### 2. Data Ingestion

The following commands are used to build a virtual machine for app deployment. First, build a docker image in the root directory:
```shell script
make image
```
Then, acquire raw data and codebook from openpsychometrics.com and upload them to s3:
```shell script
make ingest
```
Next, create the schema for a user record table in a database. Run the following command to set up the table in RDS:
```shell script
make create_db_rds
```
Alternatively, you can create the table in a local sqlite database for development purposes:
```shell script
make create_db_local
```
Note that the app requires a mysql database for advanced querying in final deployment.

As mentioned in <b>Step 1</b>, you may also specify your own database connection string with the `SQLALCHEMY_DATABASE_URI` environment variable, in the format of `"{conn_type}://{user}:{password}@{host}:{port}/{db_name}"`:
```shell script
make create_db_custom
```
When using AWS RDS, make sure that you are connected to the Northwestern VPN.

#### 3. Offline Modeling & Seed User Upload

Now, we download data from s3, perform factor analysis (feature generation) and cluster analysis (user personality group assginment), upload trained models to s3, and load seed user records (100 anonymized user profiles) into RDS with the following command:
```sh
make upload_seed
```

#### 4. Database Manipulation
From here on, you have the option to examine the database within the mysql interface. If you haven't already done so, initialize a docker image:
```sh
make mysql_init
```
Log into the interactive interface with the following command:
```sh
make mysql
```
Within the dashboard, select the database that houses the user record table, print the table names in the database, and print the table schema with the following commands respectively:
```mysql
use <database_name>;
show tables;
describe <table_name>;
```
You may also perform regular SQL queries here.

During development, you may execute the following commands to delete all records from the table or drop the table from the database:
```sh
make clear_table
make drop_table
```
Please do not execute these two commands when the app is deployed.

#### 5. Modeling Pipeline and Testing

Although you should run `make upload_seed` to deploy the app (which automatically trains and saves the model for you), you have the additional option to run the model pipeline offline in development setting. First, download the ingested data from s3:
```sh
make modeling_data
```
Then, generate features with factor analysis:
```sh
make modeling_features
```
Next, assign records to different groupings with cluster analysis:
```sh
make modeling_train
```
Finally, ensure model reproducibility with unit tests:
```sh
make modeling_test
```
The data download and feature generation steps will write csv files to the `test/` folder. The cluster analysis step will print the first 5 cluster assignment results. The unit tests download raw data from s3, perform the modeling steps, make cluster prediction on a custom row, and compare the results with the trained models we previously saved to s3. You may also change the default model hyperparameter settings in `config/modeling.yaml`.

After model tuning and testing, you may remove the csv files created in the `test/` folder:
```sh
make modeling_clear
```
You may also choose to complete all the steps in this section with one simple command:
```sh
make modeling
```

#### 6. App Deployment

As soon as you load the seed user data to RDS in <b>Step 3</b>, you may start running the flask app with the following command:
```sh
make run_app
```
You should now be able to access the app at http://0.0.0.0:5000/ in your browser.

In lieu of running the individual commands in <b>Step 2-3 and Step 6</b>, you may also set up and launch the app from scratch with one command:
```sh
make app_init
```
Note that this step uses an RDS database.

During the development phase, after you finish running the app, you may remove your RDS table, your docker containers and images with the following command:
```sh
make app_reset
```
Please do not execute this command in production setting unless you are tearing down the app.
