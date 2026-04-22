from rest_framework.views import APIView
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from core.pagination import CustomPagination
from core.responses import success_response, error_response
from apps.managements.serializers.input import (
    VideoCreateInputSerializerAdmin
)
from apps.managements.services import (
    get_video_object_by_id,
    get_all_video_list,
    create_videos_services,
    update_video_services,
    delete_video_services,
    VideoNotFoundError,
)
from apps.managements.serializers.output import (
    VideoOutputSerialzerAdmin
)

import logging
from django.db import IntegrityError


logger = logging.getLogger(__name__)



class ViewManagementViewAdmin(APIView):
    permission_classes = [IsAdminUser]
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    pagination_class = CustomPagination
    
    def get(self, request, pk = None):

        if pk:
            try:
                video_object = get_video_object_by_id(pk)
                serializer = VideoOutputSerialzerAdmin(video_object)
                return success_response(
                    "Video retrieved successfully.",
                    status_code=status.HTTP_200_OK,
                    data=serializer.data,
                )
            except Exception as e:
                return error_response(
                    "Requested video not found.",
                    status_code=status.HTTP_404_NOT_FOUND,
                )

        keyword = request.GET.get('search')  
        if keyword:     
            videos = get_all_video_list(keyword = keyword)
        else:
            videos = get_all_video_list()

        paginator = self.pagination_class()
        paginated_products = paginator.paginate_queryset(videos, request)
        serializer = VideoOutputSerialzerAdmin(paginated_products, many=True)
        return paginator.get_paginated_response(serializer.data)
    def post(self, request, pk=None):
        if pk is not None:
            return error_response(
                "Method not allowed on video detail endpoint.",
                status.HTTP_405_METHOD_NOT_ALLOWED,
            )

        # Build a shallow, mutable copy of request data to avoid deepcopying file objects
        data = {}
        for key in request.data:
            values = request.data.getlist(key)
            data[key] = values if len(values) > 1 else values[0]

        videos = request.FILES.getlist("videos")
        trailers = request.FILES.getlist("trailers")
        thumbnail = request.FILES.get("thumbnail")

        if videos:
            data["videos"] = videos

        if trailers:
            data["trailers"] = trailers

        if thumbnail:
            data["thumbnail"] = thumbnail

        serializer = VideoCreateInputSerializerAdmin(data=data)
        if not serializer.is_valid():
            return error_response(
                "Video data validation failed.",
                status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors,
            )

        try:
            video = create_videos_services(serializer.validated_data)
            output_serializer = VideoOutputSerialzerAdmin(video)
            return success_response(
                "Video created successfully.",
                status.HTTP_201_CREATED,
                data=output_serializer.data,
            )

        except IntegrityError as exc:
            logger.warning(f"Integrity error: {exc}")
            return error_response(
                "A video with the same unique attributes already exists.",
                status.HTTP_400_BAD_REQUEST,
            )
        except Exception as exc:
            logger.error(f"Error creating video: {exc}", exc_info=True)
            return error_response(
                "Unable to create the video at this time. Please try again later.",
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def put(self, request, pk=None):
        return self._update(request, pk, partial=False)

    def patch(self, request, pk=None):
        return self._update(request, pk, partial=True)

    def delete(self, request, pk=None):
        if pk is None:
            return error_response(
                "Video ID is required for delete operations.",
                status.HTTP_400_BAD_REQUEST,
            )

        try:
            delete_video_services(pk)
            return success_response(
                "Video deleted successfully.",
                status.HTTP_200_OK,
            )
        except VideoNotFoundError:
            return error_response(
                "Requested video not found.",
                status.HTTP_404_NOT_FOUND,
            )
        except Exception as exc:
            logger.error(f"Error deleting video {pk}: {exc}", exc_info=True)
            return error_response(
                "Unable to delete the video at this time. Please try again later.",
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _update(self, request, pk, partial: bool):
        if pk is None:
            return error_response(
                "Video ID is required for update operations.",
                status.HTTP_400_BAD_REQUEST,
            )

        # Build a shallow, mutable copy of request data to avoid deepcopying file objects
        data = {}
        for key in request.data:
            values = request.data.getlist(key)
            data[key] = values if len(values) > 1 else values[0]

        videos = request.FILES.getlist("videos")
        trailers = request.FILES.getlist("trailers")
        thumbnail = request.FILES.get("thumbnail")

        if videos:
            data["videos"] = videos

        if trailers:
            data["trailers"] = trailers

        if thumbnail:
            data["thumbnail"] = thumbnail

        serializer = VideoCreateInputSerializerAdmin(data=data, partial=partial, context={"video_id": pk})
        if not serializer.is_valid():
            return error_response(
                "Video data validation failed.",
                status.HTTP_400_BAD_REQUEST,
                errors=serializer.errors,
            )

        try:
            video = update_video_services(pk, serializer.validated_data, partial=partial)
            output_serializer = VideoOutputSerialzerAdmin(video)
            return success_response(
                "Video updated successfully.",
                status.HTTP_200_OK,
                data=output_serializer.data,
            )
        except VideoNotFoundError:
            return error_response(
                "Requested video not found.",
                status.HTTP_404_NOT_FOUND,
            )
        except IntegrityError as exc:
            logger.warning(f"Integrity error while updating video {pk}: {exc}")
            return error_response(
                "A video with the same unique attributes already exists.",
                status.HTTP_400_BAD_REQUEST,
            )
        except Exception as exc:
            logger.error(f"Error updating video {pk}: {exc}", exc_info=True)
            return error_response(
                "Unable to update the video at this time. Please try again later.",
                status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        
        

