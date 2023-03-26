from google.cloud import automl
import os

# TODO(developer): Uncomment and set the following variables
project_id = "60133537466"
model_id = "IOD712906846775541760"

prediction_client = automl.PredictionServiceClient()

# Get the full path of the model.
model_full_id = automl.AutoMlClient.model_path(
    project_id, "us-central1", model_id)


def object_recognition(img):
    image = automl.Image(image_bytes=img)
    payload = automl.ExamplePayload(image=image)

    # params is additional domain-specific parameters.
    # score_threshold is used to filter the result
    # https://cloud.google.com/automl/docs/reference/rpc/google.cloud.automl.v1#predictrequest
    params = {"score_threshold": "0.5"}

    request = automl.PredictRequest(
        name=model_full_id, payload=payload, params=params)
    response = prediction_client.predict(request=request)
    return response.payload


# y = 0.0666x^(-0.987) (x: 사진에 비친 물체의 폭, y: 물체까지의 거리)
def getDistanceByWidth(width):
    return round(0.0666 * (width ** -0.987), 2)


if __name__ == "__main__":
    file_paths = [f'./img/{file}' for file in os.listdir('./img')]
    for file_path in file_paths:
        with open(file_path, "rb") as content_file:
            content = content_file.read()
            for result in object_recognition(content):
                score = result.image_object_detection.score
                vertices = result.image_object_detection.bounding_box.normalized_vertices
                width = vertices[1].x - vertices[0].x
                print(file_path, width, getDistanceByWidth(width), score)

        print()
