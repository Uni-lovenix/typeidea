from django.contrib import admin
from django.urls import reverse
from django.utils.html import format_html

from .models import Post, Category, Tag
from .adminforms import PostAdminForm
from typeidea.custom_site import custom_site



# 控制在分类页也可以修改文章
class PostInline(admin.StackedInline):
    fields = ('title', 'desc')
    extra = 1
    model = Post


@admin.register(Category, site=custom_site)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [PostInline, ]

    list_display = ('name', 'status', 'is_nav', 'created_time')
    fields = ('name', 'status', 'is_nav')

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(CategoryAdmin, self).save_model(request, obj, form, change)


@admin.register(Tag, site=custom_site)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'status', 'created_time')
    fields = ('name', 'status')

    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(TagAdmin, self).save_model(request, obj, form, change)


@admin.register(Post, site=custom_site)
class PostAdmin(admin.ModelAdmin):
    form = PostAdminForm

    list_display = ('title', 'category', 'status', 'created_time', 'operator')
    list_display_links = []

    list_filter = ['category']
    search_fields = ['title', 'category__name']

    actions_on_top = True
    actions_on_bottom = True

    save_on_top = True

    exclude = ('owner',)

    '''
    fields = (
        ('category', 'title'),
        'desc',
        'status',
        'content',
        'tag',
    )
    '''

    fieldsets = (
        ('基础配置', {
            'description': '基础配置描述',
            'fields': (
                ('title', 'category'),
                'status',
            ),
        }),
        ('内容', {
            'fields': (
                'desc',
                'content',
            ),
        }),
        ('额外信息', {
            'classes': ('wide',),
            'fields': ('tag',),
        })
    )

    filter_vertical = ('tag', )

    def operator(self, obj):
        return format_html(
            '<a href="{}">编辑</a>',
            reverse('cus_admin:blog_post_change', args=(obj.id,))
        )
    operator.short_description = '操作'

    class Media:
        css = {
            'all': ('https://cdn.bootcss.com/bootstrap/4.0.0-beta.2/css/bootstrap.min.css',),
        }
        js = ('https://cdn.bootcss.com/bootstrap/4.0.0-beta.2/js/bootstrap.bundle.js',)
    
    def save_model(self, request, obj, form, change):
        obj.owner = request.user
        return super(PostAdmin, self).save_model(request, obj, form, change)


class CategoryOwnerFilter(admin.SimpleListFilter):

    title = '分类过滤器'
    parameter_name = 'owner_category'

    def lookups(self, request, model_admin):
        return Category.objects.filter(owner=request.user).value_list('id', 'name')

    def queryset(self, request, queryset):
        category_id = self.value()
        if category_id:
            return queryset.filter(category_id=self.value())
        return queryset



