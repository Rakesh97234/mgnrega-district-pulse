FROM eclipse-temurin:17-jdk-jammy
ARG JAR_FILE=target/backend.jar
COPY target/backend.jar /app/backend.jar
ENTRYPOINT ["java","-jar","/app/backend.jar"]
