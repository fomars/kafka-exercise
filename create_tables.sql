CREATE extension timescaledb cascade;

create table website (
                         id serial primary key,
                         url text unique
);

create table availability_data (
                                   ts timestamp not null,
                                   website_id int references website(id),
                                   response_time int,
                                   http_code int,
                                   regex_matches boolean,
                                   unique(ts, website_id)
);

SELECT create_hypertable('availability_data', 'ts');

