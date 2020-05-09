// .vuepress/config.js
module.exports = {
    base: '/books/serverless-aws-functional-programming/',
    themeConfig: {
      displayAllHeaders: false,
      sidebarDepth: 2,
      sidebar: [
        {
          title: 'Introduction',   // required
          path: '/',      // optional, which should be a absolute path.
          sidebarDepth: 2,    // optional, defaults to 1
          children: []
        },
        {
          title: `Chapter 1: What We're Building`,
          path: '/chapter1/',
          sidebarDepth: 2,
          children: [
            '/chapter1/asteroid_mining',
            '/chapter1/architecture'
          ]
        },
        {
            title: `Chapter 2: AWS SAM - Serverless Application Model`,
            path: '/chapter2/',
            sidebarDepth: 2,
            children: [
              '/chapter2/setup_a_project',
              '/chapter2/explore',
              '/chapter2/play',
              '/chapter2/invoke',
              '/chapter2/deploy',
              '/chapter2/inspect',
            ]
        },
        {
            title: `Chapter 3: Lambda - Download Benner Equations`,
            path: '/chapter3/',
            sidebarDepth: 2,
            children: [
              '/chapter3/rename',
              '/chapter3/download',
              '/chapter3/contract',
              '/chapter3/deploy',
              '/chapter3/clean',
            ]
        },
        {
            title: `Chapter 4: Step Function`,
            path: '/chapter4/',
            sidebarDepth: 2,
            children: [
              '/chapter4/editor',
              '/chapter4/inline',
              '/chapter4/wiring',
              '/chapter4/test',
              '/chapter4/error_types',
              '/chapter4/permissions',
            ]
        },
        {
          title: `Chapter 5: Lambda - Download Exoplanets`,
          path: '/chapter5/',
          sidebarDepth: 2,
          children: [
            '/chapter5/copy_pasta_coding',
            '/chapter5/strengthening_the_lambda_contract',
            '/chapter5/are_we_good',
            '/chapter5/step_function_retry',
          ]
        },
        {
          title: `Chapter 6: Lambda - Parse Masses`,
          path: '/chapter6/',
          sidebarDepth: 2,
          children: [
            '/chapter6/composing_functions',
            '/chapter6/first_version',
            '/chapter6/results',
            '/chapter6/installing_and_using_python_libraries',
            '/chapter6/rewrite',
          ]
        },
        {
          title: `Chapter 7: Parallel in Step Function`,
          path: '/chapter7/',
          sidebarDepth: 2,
          children: [
            '/chapter7/destroy_all_globals',
            '/chapter7/step_function_input',
            '/chapter7/latest_asteroids_lambda',
            '/chapter7/upload_partial_application',
            '/chapter7/zip_stream',
          ]
        },
      ]
    }
  }
