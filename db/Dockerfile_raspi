FROM arm32v7/postgres:10
USER postgres
COPY postgresql.conf /etc/postgresql
CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]