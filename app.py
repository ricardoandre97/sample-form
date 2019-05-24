import psycopg2
import os
from flask import Flask, render_template, request

app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def index():
    _vars = {}
    if request.method == 'POST':
        form = request.form
        # Validate some basic input
        if (
            not form['fname'] or not form['lname'] or 'pet' not in form
        ):
            _vars['info'] = 'All the fields are mandatory. Please, try again.'

        else:

            fname = form['fname'].lower()
            lname = form['lname'].lower()
            pet = form['pet']

            # Try to save the input in the db
            try:
                pwd = os.environ['POSTGRES_PASSWORD']
                db_host = os.environ['DB_HOST']
                db_port = os.environ['DB_PORT']
                db_name = os.environ['DB_NAME']
                db_user = os.environ['DB_USER']
                table = os.environ['TABLE_NAME']

                # Create the db connection
                connection = psycopg2.connect(
                    user=db_user, password=pwd, host=db_host, port=db_port,
                    database=db_name
                )
                cursor = connection.cursor()

                # Set the query to insert the record if it doesn't exist
                postgres_insert_query = (
                    f"INSERT INTO {table} (NAME, LASTNAME, CATS_OR_DOGS) "
                    f"SELECT * FROM (SELECT '{fname}', '{lname}', '{pet}') AS tmp "
                    "WHERE NOT EXISTS ("
                    f"    SELECT NAME FROM {table} WHERE NAME = '{fname}' "
                    ") LIMIT 1;"
                )
                # Try to insert the record
                cursor.execute(postgres_insert_query)
                connection.commit()

                # See if the record was inserted or not
                exists = False
                if cursor.rowcount == 0:
                    # Record was not inserted since name already existed
                    exists = True

                if not exists:
                    # Great! It was saved
                    _vars['info'] = 'Data sucessfully saved!'
                else:
                    _vars['info'] = f'Sorry, {fname} is already saved.'
            except (Exception, psycopg2.Error) as error:
                if connection:
                    print(error)
                    _vars['info'] = (
                        'Sorry, something went wrong when saving your data :('
                    )
            finally:
                # Close the db connection
                if connection:
                    cursor.close()
                    connection.close()

    return render_template('index.html', result=_vars)


if __name__ == '__main__':
    app.run(host='0.0.0.0')
