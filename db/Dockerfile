FROM postgres:10
USER postgres
COPY postgresql.conf /etc/postgresql
ENV TZ="America/Sao_Paulo"
CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]