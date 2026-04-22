from django.db import transaction
from apps.managements.models import Video, VideoMedia
from django.db.models import Q


class VideoNotFoundError(Exception):
    pass


def get_video_object_by_id(pk: int) -> Video:
    video = Video.objects.prefetch_related("videos", "trailers").filter(pk=pk).first()
    if not video:
        raise VideoNotFoundError(f"Video with id {pk} does not exist.")
    return video


def get_all_video_list(keyword: str | None = None) -> list[Video]:
    queryset = Video.objects.all().order_by("-created_at")

    if keyword:
        queryset = queryset.filter(
            Q(title__icontains=keyword) |
            Q(category__icontains=keyword) |
            Q(status__icontains=keyword) |
            Q(description__icontains=keyword)
        )

    return queryset


def _create_video_images(files):
    return [VideoMedia.objects.create(file=file_obj) for file_obj in files]


def create_videos_services(validated_data: dict) -> Video:
    videos = validated_data.pop("videos", [])
    trailers = validated_data.pop("trailers", [])
    thumbnail = validated_data.pop("thumbnail", None)

    with transaction.atomic():
        video = Video.objects.create(**validated_data)

        if videos:
            video_medias = _create_video_images(videos)
            video.videos.set(video_medias)

        if trailers:
            video_medias = _create_video_images(trailers)
            video.trailers.set(video_medias)

        if thumbnail:
            video.thumbnail = thumbnail
            video.save(update_fields=["thumbnail"])

        return Video.objects.prefetch_related("videos", "trailers").get(pk=video.pk)


def update_video_services(video_id: int, validated_data: dict, partial: bool = False) -> Video:
    videos = validated_data.pop("videos", None)
    trailers = validated_data.pop("trailers", None)
    thumbnail = validated_data.pop("thumbnail", None)

    with transaction.atomic():
        video = Video.objects.select_for_update().filter(pk=video_id).first()
        if not video:
            raise VideoNotFoundError(f"Video with id {video_id} does not exist.")

        for field, value in validated_data.items():
            setattr(video, field, value)

        if thumbnail is not None:
            video.thumbnail = thumbnail

        video.save()

        if videos is not None:
            new_medias = _create_video_images(videos)
            video.videos.set(new_medias)

        if trailers is not None:
            new_trailers = _create_video_images(trailers)
            video.trailers.set(new_trailers)

        return Video.objects.prefetch_related("videos", "trailers").get(pk=video.pk)


def delete_video_services(video_id: int) -> None:
    with transaction.atomic():
        video = Video.objects.select_for_update().filter(pk=video_id).first()
        if not video:
            raise VideoNotFoundError(f"Video with id {video_id} does not exist.")

        media_ids = list(video.videos.values_list("id", flat=True)) + list(video.trailers.values_list("id", flat=True))
        video.delete()

        if media_ids:
            VideoMedia.objects.filter(id__in=media_ids).filter(video_contents__isnull=True, video_trailers__isnull=True).delete()
from django.db import transaction
from apps.managements.models import Video, VideoMedia
from django.db.models import Q

class VideoNotFoundError(Exception):
    pass

def get_video_object_by_id(pk:int) -> Video:

    video = Video.objects.prefetch_related("videos", "trailers").filter(pk=pk).first()
    if not video:
        raise VideoNotFoundError(f"Video with id {pk} does not exist.")
    return video




def get_all_video_list(keyword=None) -> list[Video]:

    queryset = Video.objects.all().order_by('-created_at')

    if keyword:
        queryset = queryset.filter(
            Q(title__icontains=keyword) |
            Q(category__icontains=keyword) |
            Q(status__icontains=keyword) |
            Q(description__icontains=keyword)
        )

    return queryset




def _create_video_images(files):
    return [VideoMedia.objects.create(file=file_obj) for file_obj in files]


def create_videos_services(validated_data:dict) -> Video:
    videos = validated_data.pop("videos", [])
    trailers = validated_data.pop("trailers", [])
    thumbnail = validated_data.pop("thumbnail", None)

  

    with transaction.atomic():
        video = Video.objects.create(**validated_data)

        if videos:
            video_medias = _create_video_images(videos)
            video.videos.set(video_medias)
        
        if trailers:
            video_medias = _create_video_images(trailers)
            video.trailers.set(video_medias)
        
        if thumbnail:
            video.thumbnail = thumbnail
            video.save(update_fields=["thumbnail"])

        return Video.objects.prefetch_related("videos", "trailers").get(pk=video.pk)
    

def update_video_services(video_id: int, validated_data: dict, partial: bool = False) -> Video:
    videos = validated_data.pop("videos", None)
    trailers = validated_data.pop("trailers", None)
    thumbnail = validated_data.pop("thumbnail", None)

    with transaction.atomic():
        video = Video.objects.select_for_update().filter(pk=video_id).first()
        if not video:
            raise VideoNotFoundError(f"Video with id {video_id} does not exist.")

        for field, value in validated_data.items():
            setattr(video, field, value)

        if thumbnail is not None:
            video.thumbnail = thumbnail

        video.save()

        if videos is not None:
            new_medias = _create_video_images(videos)
            video.videos.set(new_medias)

        if trailers is not None:
            new_trailers = _create_video_images(trailers)
            video.trailers.set(new_trailers)

        return Video.objects.prefetch_related("videos", "trailers").get(pk=video.pk)


def delete_video_services(video_id: int) -> None:
    with transaction.atomic():
        video = Video.objects.select_for_update().filter(pk=video_id).first()
        if not video:
            raise VideoNotFoundError(f"Video with id {video_id} does not exist.")

        media_ids = list(video.videos.values_list("id", flat=True)) + list(video.trailers.values_list("id", flat=True))
        video.delete()

        if media_ids:
            VideoMedia.objects.filter(id__in=media_ids).filter(video_contents__isnull=True, video_trailers__isnull=True).delete()
