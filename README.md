# Find Like-Minded Souls: A People-to-People Reciprocal Recommendation System

Qiana Yang, with QA contributions from Louis-Charles Généreux

Northwestern University MS in Analytics Course Project: Analytics Value Chain

## Project Charter

Perhaps you are an MSiA student new to the program, hoping to find compatible partners for group projects. Or perhaps you are a singleton in search of a perfect match without resorting to traditional dating apps. Whether you're in need of a new friend or looking to form deep bonds with a like-minded person, a reciprocal recommendation system can give you a little nudge to build a meaningful connection with the right person at the right time. 

**Vision**

In today's fast-paced environment, we don't always have the opportunity to get to know everyone in our community beyond a superficial level. However, we are constantly expected to work with others as part of a team. Business projects and personal life can become dangerously stressful when you and your partner(s) have drastically incompatible personalities.

This app aims to help users find other users with similar personality traits. If deployed in professional settings, the app can also help users make informed decisions about who to team up with on a business project.

**Mission**

Each app user will fill out Cattell's 16 personality survey to the best of their ability. Based on the survey results, the recommender will map the user to a vector in an embedding space with factor and clustering analyses. The recommender will then output a list of new user profiles based on their proximity to the first user profile.

Although the app will ultimately rely on real-time data from its user base, it will use a static dataset for the initial launch. The dataset in question consists of approximately 50000 rows of anonymized user survey results published on [openpsychometrics.org](openpsychometrics.org) (download [here](http://openpsychometrics.org/_rawdata/16PF.zip)). An interactive version of the survey can be found at [openpsychometrics.org/tests/16PF.php](https://openpsychometrics.org/tests/16PF.php).

**Success criteria**

*Machine learning performance metric:* 

Because the recommendation system employs unsupervised learning algorithms, we will use a number of non-traditional model/feature selection metrics to ensure the robustness of our approach. For now, we will rely on the silhoutte score and reduction in SSE to select the optimal number of clusters, and use the Kaiser criteria for dimensionality reduction and factor analysis. Since the method is unsupervised, there's no hard success threshold we can aim for &ndash; however, I hope to retain features that capture around 95% of the variation in the data as I perform factor analysis.

Once the app is launched, we can then calculate the precision, recall, AUC, and F1 score of our recommendation engine based on dynamic user feedback. Tinder's current algorithm has an astonishing AUC of 90% and F1 of 85% &ndash; these are the numbers I'll be aiming for. 

*Business metric:*

We can measure the business value of the app based on user acquisition rates, churn rates, user engagement metrics (e.g. average session duration and total time on app), and of course, the number of successful matches made based on user feedback (e.g. number of successful matches divided by total time on app per user).

## Running the App (Midproject Checkpoint)
### 1. Initialize the database 

#### Create the database 

**Data download and S3 upload instructions**

We are going to download a static, public dataset, extract the zip file in Python, and upload the extracted files (a 12MB csv file and a corresponding data codebook that explains different fields in the data columns) to an S3 bucket without saving the files locally. The command to perform the task is as follows:

```shell script
python run.py ingest -b <s3_bucket_name> [-c] [<codebook_path>] [-d] [<data_path>]
```
When running the command, make sure you have AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY set as environment variables (i.e. `os.environ.get('AWS_ACCESS_KEY_ID')` or `os.environ.get('AWS_SECRET_ACCESS_KEY')` do not return `None`). You can do so via the following command:

```shell script
export AWS_ACCESS_KEY_ID='<aws_access_key_id>'
export AWS_SECRET_ACCESS_KEY='<aws_secret_access_key>'
```

Note that you must specify a valid *s3_bucket_name* for successful data upload. You may also specify custom codebook path or data path in S3. The default filepaths are `'raw/codebook.txt'` and `'raw/data.csv'` respectively. 

You also need to be connected to the Northwestern VPN to run the command.

Finally, you may reset the logging configuration level in *config/flaskconfig.py*.

**Database schema creation instructions**

First, you need to set environment variables. Depending on which variables you have provided, different default values for SQLAlchemy's connection engine string will be set. You may specify your engine string with the environment variable `SQLALCHEMY_DATABASE_URI`.

If `SQLALCHEMY_DATABASE_URI` is not provided as an environment variable, then the system will be looking for the environment variable `MYSQL_HOST` and attempt to create the database on RDS. For the command to successfully run at this step, you also need to set the following environment variables: MYSQL_PORT, MYSQL_USER, MYSQL_PASSWORD, and DATABASE_NAME.

If none of these variables are provided, the system will create a local sqlite database at the default location `'./data/data.db'`. 

Finally, you may specify your own engine string in lieu of providing an environment variable. To do so, see the command line argument below. Note that if you specify your own engine string, that will override the default engine strings created by my script even if you have also created the environment variables I've talked about above.

Once you have configured your environment variables, run the following command at root directory: 
```sh
python run.py create_db [-g] [<engine string>]
```
If you want to use your own custom engine string instead, simply specify the `-g` optional argument. Keep in mind that the format for engine strings is `{conn_type}://{user}:{password}@{host}:{port}/{db_name}`.

Caveat: if you try to create a table that already exists (i.e. having the same table name) in the database you specified, no new table would be created. In other words, the old table would remain the same as it was. To override the old table, you need to drop the table first within the mysql interface and then re-run the command above.

**Run the Above Pipeline in Docker**

First, clone the repository and navigate to the root directory. Run the following commands to build a Docker image:
```sh
docker build -t qiana_project .
```
Once a Docker image is built, we will upload raw data to S3 with the following command:
```sh
docker run -it \
    -e AWS_ACCESS_KEY_ID \
    -e AWS_SECRET_ACCESS_KEY \
    qiana_project run.py ingest \
    -b <s3_bucket_name> \
    [-c] [<codebook_path>] \
    [-d] [<data_path>]
```
Then, create database schema in RDS (non-locally) with the following command:
```sh
docker run -it \
    -e MYSQL_HOST \
    -e MYSQL_PORT \
    -e MYSQL_USER \
    -e MYSQL_PASSWORD \
    -e DATABASE_NAME \
    qiana_project run.py create_db \
    [-g] [<engine_string>]
```
You may also create the schema locally in the `data` directory (default filepath is `data/data.db`):
```sh
docker run -it \
    qiana_project run.py create_db \
    [-g] [<engine_string>]
```
Or, specify your own engine string and output path with the `SQLALCHEMY_DATABASE_URI` environment variable:
```shell script
docker run -it \
    -e SQLALCHEMY_DATABASE_URI \
    qiana_project run.py create_db \
    [-g] [<engine_string>]
```
If you are a Windows user, add `winpty` before each `docker run` statement. 

### To Be Edited...
## Content

<!-- toc -->

- [Directory structure](#directory-structure)
- [Running the app](#running-the-app)
  * [1. Initialize the database](#1-initialize-the-database)
    + [Create the database with a single song](#create-the-database-with-a-single-song)
    + [Adding additional songs](#adding-additional-songs)
    + [Defining your engine string](#defining-your-engine-string)
      - [Local SQLite database](#local-sqlite-database)
  * [2. Configure Flask app](#2-configure-flask-app)
  * [3. Run the Flask app](#3-run-the-flask-app)
- [Running the app in Docker](#running-the-app-in-docker)
  * [1. Build the image](#1-build-the-image)
  * [2. Run the container](#2-run-the-container)
  * [3. Kill the container](#3-kill-the-container)
  * [Workaround for potential Docker problem for Windows.](#workaround-for-potential-docker-problem-for-windows)

<!-- tocstop -->

## Directory structure 

```
├── README.md                         <- You are here
├── api
│   ├── static/                       <- CSS, JS files that remain static
│   ├── templates/                    <- HTML (or other code) that is templated and changes based on a set of inputs
│   ├── boot.sh                       <- Start up script for launching app in Docker container.
│   ├── Dockerfile                    <- Dockerfile for building image to run app  
│
├── config                            <- Directory for configuration files 
│   ├── local/                        <- Directory for keeping environment variables and other local configurations that *do not sync** to Github 
│   ├── logging/                      <- Configuration of python loggers
│   ├── flaskconfig.py                <- Configurations for Flask API 
│
├── data                              <- Folder that contains data used or generated. Only the external/ and sample/ subdirectories are tracked by git. 
│   ├── external/                     <- External data sources, usually reference data,  will be synced with git
│   ├── sample/                       <- Sample data used for code development and testing, will be synced with git
│
├── deliverables/                     <- Any white papers, presentations, final work products that are presented or delivered to a stakeholder 
│
├── docs/                             <- Sphinx documentation based on Python docstrings. Optional for this project. 
│
├── figures/                          <- Generated graphics and figures to be used in reporting, documentation, etc
│
├── models/                           <- Trained model objects (TMOs), model predictions, and/or model summaries
│
├── notebooks/
│   ├── archive/                      <- Develop notebooks no longer being used.
│   ├── deliver/                      <- Notebooks shared with others / in final state
│   ├── develop/                      <- Current notebooks being used in development.
│   ├── template.ipynb                <- Template notebook for analysis with useful imports, helper functions, and SQLAlchemy setup. 
│
├── reference/                        <- Any reference material relevant to the project
│
├── src/                              <- Source data for the project 
│
├── test/                             <- Files necessary for running model tests (see documentation below) 
│
├── app.py                            <- Flask wrapper for running the model 
├── run.py                            <- Simplifies the execution of one or more of the src scripts  
├── requirements.txt                  <- Python package dependencies 
```



### 2. Configure Flask app 

`config/flaskconfig.py` holds the configurations for the Flask app. It includes the following configurations:

```python
DEBUG = True  # Keep True for debugging, change to False when moving to production 
LOGGING_CONFIG = "config/logging/local.conf"  # Path to file that configures Python logger
HOST = "0.0.0.0" # the host that is running the app. 0.0.0.0 when running locally 
PORT = 5000  # What port to expose app on. Must be the same as the port exposed in app/Dockerfile 
SQLALCHEMY_DATABASE_URI = 'sqlite:///data/tracks.db'  # URI (engine string) for database that contains tracks
APP_NAME = "penny-lane"
SQLALCHEMY_TRACK_MODIFICATIONS = True 
SQLALCHEMY_ECHO = False  # If true, SQL for queries made will be printed
MAX_ROWS_SHOW = 100 # Limits the number of rows returned from the database 
```

### 3. Run the Flask app 

To run the Flask app, run: 

```bash
python app.py
```

You should now be able to access the app at http://0.0.0.0:5000/ in your browser.

## Running the app in Docker 

### 1. Build the image 

The Dockerfile for running the flask app is in the `app/` folder. To build the image, run from this directory (the root of the repo): 

```bash
 docker build -f app/Dockerfile -t pennylane .
```

This command builds the Docker image, with the tag `pennylane`, based on the instructions in `app/Dockerfile` and the files existing in this directory.
 
### 2. Run the container 

To run the app, run from this directory: 

```bash
docker run -p 5000:5000 --name test pennylane
```
You should now be able to access the app at http://0.0.0.0:5000/ in your browser.

This command runs the `pennylane` image as a container named `test` and forwards the port 5000 from container to your laptop so that you can access the flask app exposed through that port. 

If `PORT` in `config/flaskconfig.py` is changed, this port should be changed accordingly (as should the `EXPOSE 5000` line in `app/Dockerfile`)

### 3. Kill the container 

Once finished with the app, you will need to kill the container. To do so: 

```bash
docker kill test 
```

where `test` is the name given in the `docker run` command.

### Example using `python3` as an entry point

We have included another example of a Dockerfile, `app/Dockerfile_python` that has `python3` as the entry point such that when you run the image as a container, the command `python3` is run, followed by the arguments given in the `docker run` command after the image name. 

To build this image: 

```bash
 docker build -f app/Dockerfile_python -t pennylane .
```

then run the `docker run` command: 

```bash
docker run -p 5000:5000 --name test pennylane app.py
```

The new image defines the entry point command as `python3`. Building the sample PennyLane image this way will require initializing the database prior to building the image so that it is copied over, rather than created when the container is run. Therefore, please **do the step [Create the database with a single song](#create-the-database-with-a-single-song) above before building the image**.

# Testing

From within the Docker container, the following command should work to run unit tests when run from the root of the repository: 

```bash
python -m pytest
``` 

Using Docker, run the following, if the image has not been built yet:

```bash
 docker build -f app/Dockerfile_python -t pennylane .
```

To run the tests, run: 

```bash
 docker run penny -m pytest
```
 
