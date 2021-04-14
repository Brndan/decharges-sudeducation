import os.path

from django import template

register = template.Library()


@register.filter("startswith")
def startswith(text, starts):
    try:
        return text.startswith(starts)
    except (TypeError, AttributeError):
        return False


@register.filter("filename")
def filename(path):
    return os.path.basename(path)


@register.filter("fa_extension")
def fa_extension(path):
    extension = path.split(".")[-1]
    if not extension:
        return "file"
    extension = extension.lower()
    if extension == "pdf":
        return "file-pdf"
    if extension in {"png", "jpg", "jpeg", "gif", "webp", "tiff", "psd", "bmp", "svg"}:
        return "file-image"
    if extension in {"doc", "docx", "odt"}:
        return "file-word"
    if extension in {"xls", "xslx", "ods"}:
        return "file-excel"
    if extension in {"ppt", "pptx", "odg"}:
        return "file-powerpoint"
    return "file"
