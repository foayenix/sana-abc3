import 'package:flutter/material.dart';
import 'package:cached_network_image/cached_network_image.dart';
import '../../config/colors.dart';
import '../../config/theme.dart';

enum SanaAvatarSize { xs, sm, md, lg, xl, xxl }

class SanaAvatar extends StatelessWidget {
  final String? imageUrl;
  final String? name;
  final SanaAvatarSize size;
  final bool showBorder;
  final bool isOnline;
  final VoidCallback? onTap;

  const SanaAvatar({
    super.key,
    this.imageUrl,
    this.name,
    this.size = SanaAvatarSize.md,
    this.showBorder = false,
    this.isOnline = false,
    this.onTap,
  });

  double get _size {
    switch (size) {
      case SanaAvatarSize.xs:
        return 24;
      case SanaAvatarSize.sm:
        return 32;
      case SanaAvatarSize.md:
        return 48;
      case SanaAvatarSize.lg:
        return 64;
      case SanaAvatarSize.xl:
        return 80;
      case SanaAvatarSize.xxl:
        return 120;
    }
  }

  double get _fontSize {
    switch (size) {
      case SanaAvatarSize.xs:
        return 10;
      case SanaAvatarSize.sm:
        return 12;
      case SanaAvatarSize.md:
        return 16;
      case SanaAvatarSize.lg:
        return 20;
      case SanaAvatarSize.xl:
        return 28;
      case SanaAvatarSize.xxl:
        return 40;
    }
  }

  String get _initials {
    if (name == null || name!.isEmpty) return '?';
    final parts = name!.trim().split(' ');
    if (parts.length >= 2) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    }
    return name![0].toUpperCase();
  }

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Stack(
        children: [
          Container(
            width: _size,
            height: _size,
            decoration: BoxDecoration(
              shape: BoxShape.circle,
              border: showBorder
                  ? Border.all(
                      color: SanaColors.white,
                      width: 3,
                    )
                  : null,
              boxShadow: showBorder
                  ? [
                      BoxShadow(
                        color: SanaColors.black.withOpacity(0.1),
                        blurRadius: 8,
                        offset: const Offset(0, 2),
                      ),
                    ]
                  : null,
            ),
            child: ClipOval(
              child: imageUrl != null && imageUrl!.isNotEmpty
                  ? CachedNetworkImage(
                      imageUrl: imageUrl!,
                      fit: BoxFit.cover,
                      placeholder: (context, url) => _buildPlaceholder(),
                      errorWidget: (context, url, error) => _buildPlaceholder(),
                    )
                  : _buildPlaceholder(),
            ),
          ),
          if (isOnline)
            Positioned(
              right: 0,
              bottom: 0,
              child: Container(
                width: _size * 0.3,
                height: _size * 0.3,
                decoration: BoxDecoration(
                  color: SanaColors.success,
                  shape: BoxShape.circle,
                  border: Border.all(
                    color: SanaColors.white,
                    width: 2,
                  ),
                ),
              ),
            ),
        ],
      ),
    );
  }

  Widget _buildPlaceholder() {
    return Container(
      color: SanaColors.primaryLight,
      child: Center(
        child: Text(
          _initials,
          style: TextStyle(
            fontSize: _fontSize,
            fontWeight: FontWeight.w600,
            color: SanaColors.primaryDark,
          ),
        ),
      ),
    );
  }
}

class SanaAvatarGroup extends StatelessWidget {
  final List<String?> imageUrls;
  final List<String?> names;
  final SanaAvatarSize size;
  final int maxDisplay;
  final VoidCallback? onTap;

  const SanaAvatarGroup({
    super.key,
    required this.imageUrls,
    this.names = const [],
    this.size = SanaAvatarSize.sm,
    this.maxDisplay = 3,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    final displayCount = imageUrls.length > maxDisplay ? maxDisplay : imageUrls.length;
    final overflow = imageUrls.length - maxDisplay;

    return GestureDetector(
      onTap: onTap,
      child: SizedBox(
        height: _getSize(),
        child: Stack(
          children: [
            for (int i = 0; i < displayCount; i++)
              Positioned(
                left: i * (_getSize() * 0.7),
                child: SanaAvatar(
                  imageUrl: imageUrls[i],
                  name: i < names.length ? names[i] : null,
                  size: size,
                  showBorder: true,
                ),
              ),
            if (overflow > 0)
              Positioned(
                left: displayCount * (_getSize() * 0.7),
                child: Container(
                  width: _getSize(),
                  height: _getSize(),
                  decoration: BoxDecoration(
                    color: SanaColors.grey200,
                    shape: BoxShape.circle,
                    border: Border.all(
                      color: SanaColors.white,
                      width: 3,
                    ),
                  ),
                  child: Center(
                    child: Text(
                      '+$overflow',
                      style: TextStyle(
                        fontSize: _getSize() * 0.35,
                        fontWeight: FontWeight.w600,
                        color: SanaColors.textSecondary,
                      ),
                    ),
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  double _getSize() {
    switch (size) {
      case SanaAvatarSize.xs:
        return 24;
      case SanaAvatarSize.sm:
        return 32;
      case SanaAvatarSize.md:
        return 48;
      case SanaAvatarSize.lg:
        return 64;
      case SanaAvatarSize.xl:
        return 80;
      case SanaAvatarSize.xxl:
        return 120;
    }
  }
}
