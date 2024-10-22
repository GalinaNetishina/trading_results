FROM node:18.20.2

WORKDIR /fastapi_app/frontend
RUN npm run dev


# FROM nginx:stable-alpine

# COPY --from=build /dist /usr/share/nginx/html
# COPY --from=build nginx.conf /etc/nginx/conf.d/default.conf
# EXPOSE 3000
# CMD [ "nginx", "-g", "daemon off;" ]