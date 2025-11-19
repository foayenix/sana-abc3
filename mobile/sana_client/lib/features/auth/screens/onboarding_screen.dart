import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/routes.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_button.dart';

class OnboardingScreen extends StatefulWidget {
  const OnboardingScreen({super.key});

  @override
  State<OnboardingScreen> createState() => _OnboardingScreenState();
}

class _OnboardingScreenState extends State<OnboardingScreen> {
  final PageController _pageController = PageController();
  int _currentPage = 0;

  final List<OnboardingPage> _pages = [
    OnboardingPage(
      icon: Icons.spa_outlined,
      title: 'Find Your Practitioner',
      description:
          'Discover evidence-based wellness practitioners tailored to your needs. Browse by specialty, location, and verified outcomes.',
      color: SanaColors.primaryDark,
    ),
    OnboardingPage(
      icon: Icons.calendar_month_outlined,
      title: 'Book with Confidence',
      description:
          'See real outcome data before you book. Schedule sessions seamlessly and manage your appointments in one place.',
      color: SanaColors.primaryMedium,
    ),
    OnboardingPage(
      icon: Icons.insights_outlined,
      title: 'Track Your Progress',
      description:
          'Monitor your health journey with personalized insights. Connect wearables and see your improvements over time.',
      color: SanaColors.primaryLight,
    ),
  ];

  @override
  void dispose() {
    _pageController.dispose();
    super.dispose();
  }

  void _nextPage() {
    if (_currentPage < _pages.length - 1) {
      _pageController.nextPage(
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeInOut,
      );
    } else {
      context.go(AppRoutes.login);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      body: SafeArea(
        child: Column(
          children: [
            // Skip button
            Align(
              alignment: Alignment.topRight,
              child: TextButton(
                onPressed: () => context.go(AppRoutes.login),
                child: Text(
                  'Skip',
                  style: SanaTextStyles.link,
                ),
              ),
            ),

            // Page content
            Expanded(
              child: PageView.builder(
                controller: _pageController,
                onPageChanged: (index) {
                  setState(() {
                    _currentPage = index;
                  });
                },
                itemCount: _pages.length,
                itemBuilder: (context, index) {
                  return _OnboardingPageView(page: _pages[index]);
                },
              ),
            ),

            // Page indicators
            Padding(
              padding: const EdgeInsets.symmetric(vertical: SanaSpacing.lg),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(
                  _pages.length,
                  (index) => AnimatedContainer(
                    duration: const Duration(milliseconds: 300),
                    margin: const EdgeInsets.symmetric(horizontal: 4),
                    width: _currentPage == index ? 24 : 8,
                    height: 8,
                    decoration: BoxDecoration(
                      color: _currentPage == index
                          ? SanaColors.primaryDark
                          : SanaColors.grey300,
                      borderRadius: BorderRadius.circular(4),
                    ),
                  ),
                ),
              ),
            ),

            // Action buttons
            Padding(
              padding: const EdgeInsets.all(SanaSpacing.lg),
              child: Column(
                children: [
                  SanaButton(
                    text: _currentPage == _pages.length - 1
                        ? 'Get Started'
                        : 'Continue',
                    onPressed: _nextPage,
                  ),
                  const SizedBox(height: SanaSpacing.md),
                  if (_currentPage == _pages.length - 1)
                    Row(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(
                          'Already have an account? ',
                          style: SanaTextStyles.bodySmall,
                        ),
                        GestureDetector(
                          onTap: () => context.go(AppRoutes.login),
                          child: Text(
                            'Sign In',
                            style: SanaTextStyles.link,
                          ),
                        ),
                      ],
                    ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class OnboardingPage {
  final IconData icon;
  final String title;
  final String description;
  final Color color;

  OnboardingPage({
    required this.icon,
    required this.title,
    required this.description,
    required this.color,
  });
}

class _OnboardingPageView extends StatelessWidget {
  final OnboardingPage page;

  const _OnboardingPageView({required this.page});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: SanaSpacing.xl),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          // Icon container
          Container(
            width: 160,
            height: 160,
            decoration: BoxDecoration(
              color: page.color.withOpacity(0.1),
              shape: BoxShape.circle,
            ),
            child: Icon(
              page.icon,
              size: 80,
              color: page.color,
            ),
          ),
          const SizedBox(height: SanaSpacing.xl),
          // Title
          Text(
            page.title,
            style: SanaTextStyles.heading1,
            textAlign: TextAlign.center,
          ),
          const SizedBox(height: SanaSpacing.md),
          // Description
          Text(
            page.description,
            style: SanaTextStyles.body.copyWith(
              color: SanaColors.textSecondary,
              height: 1.6,
            ),
            textAlign: TextAlign.center,
          ),
        ],
      ),
    );
  }
}
