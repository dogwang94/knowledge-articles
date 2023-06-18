FROM nginx:latest

# RUN rm /etc/nginx/conf.d/default.conf
COPY ./nginx/nginx.conf /etc/nginx/conf.d

# COPY --from=base /app /app

EXPOSE 80

# CMD ["sh", "-c", "nginx app:app -w 4 -b 0.0.0.0:80"]
