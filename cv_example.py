# Example Usage: Optimizing CV for Backend Developer Role
# This shows how to use the PowerCV system with a sample CV

import json

from app.services.cv_analyzer import CVAnalyzer
from app.services.cv_optimizer import CVOptimizer
from app.services.workflow_orchestrator import CVWorkflowOrchestrator

# Sample CV text (depersonalized)
SAMPLE_CV = """
Name: John Doe
Position: Software / Systems / Backend Developer / Tech & Engineering Professional
Birthdate: 01.01.1990 (35 y.o.)
Address: 123 Main St, Amsterdam, The Netherlands
Email: john.doe@example.com
Phone: +31 6 12345678

PROFESSIONAL SUMMARY
Tech & Engineering Professional with over 10 years of experience in backend development 
and procurement, renowned for pioneering innovative solutions and optimizing system efficiencies.
Masterfully skilled in Python, DevOps, and Dockerized microservices, fostering a collaborative 
and dynamic team environment. Passionate about continuous learning, with a keen interest in 
expanding expertise within the evolving Dutch tech landscape.

EMPLOYMENT HISTORY

PYTHON BACKEND DEVELOPER - Jan 2023 - Present
Freelance Remote
• Develop REST APIs with Flask, boosting backend efficiency and response times.
• Design Dockerized microservices for scalable deployments, enhancing system reliability.
• Create automated ETL pipelines, ensuring flawless data processing and deployment success.
• Conduct code reviews to optimize application stability and performance.
• Collaborate with frontend teams for seamless integration, improving project delivery timelines.
• Mentor junior developers, nurturing their skills and promoting a positive, collaborative team environment.

[Additional roles...]

SKILLS
Programming & Scripting: Python, Go, TypeScript
Web Frameworks & APIs: Flask, FastAPI, Django, REST APIs, GraphQL
Databases: PostgreSQL, MySQL, MongoDB, Redis, ElasticSearch
Cloud & DevOps: AWS, Docker, Kubernetes, CI/CD Pipelines, Jenkins, GitHub Actions
"""


# Example job description
SAMPLE_JD = """
Senior Backend Developer - Python & Microservices

About the Role:
We're seeking an experienced Backend Developer to join our engineering team in Amsterdam.
You'll be responsible for designing and implementing scalable microservices, working with
modern cloud infrastructure, and mentoring junior developers.

Requirements:
• 3+ years of Python development experience
• Expert knowledge of Flask or FastAPI frameworks
• Strong experience with Docker and Kubernetes
• REST API design and GraphQL knowledge
• PostgreSQL or MySQL database expertise
• CI/CD pipeline setup and maintenance (Jenkins, GitHub Actions)
• Experience with AWS or GCP cloud platforms
• Test-driven development practices
• Strong communication skills and team collaboration

Nice to Have:
• Experience with Go or TypeScript
• Redis caching implementation
• Microservices architecture patterns
• ElasticSearch integration
• Experience mentoring junior developers

What We Offer:
• Competitive salary (€60,000 - €85,000)
• Remote work flexibility
• Professional development budget
• Modern tech stack
• Collaborative team culture
"""


def example_1_analyze_cv():
    """Example 1: Analyze sample CV against job description"""
    print("=" * 70)
    print("EXAMPLE 1: CV Analysis")
    print("=" * 70)
    
    analyzer = CVAnalyzer()
    
    try:
        result = analyzer.analyze(SAMPLE_CV, SAMPLE_JD)
        
        print("\n Analysis completed successfully!")
        print(f"\n ATS Score: {result['ats_score']}/100")
        print(f"\n Summary: {result['summary']}")
        
        print("\n Matched Keywords:")
        for kw in result['keyword_analysis']['matched_keywords'][:5]:
            print(f"  • {kw['keyword']} (JD: {kw['jd_mentions']}x, CV: {kw['cv_mentions']}x)")
        
        print("\n  Missing Critical Keywords:")
        for kw in result['keyword_analysis']['missing_critical'][:5]:
            print(f"  • {kw['keyword']} ({kw['category']}) - Priority: {kw['priority']}")
        
        print("\n Strengths:")
        for strength in result['strengths'][:3]:
            print(f"  • {strength}")
        
        print("\n Top Recommendations:")
        for rec in result['recommendations'][:3]:
            print(f"  • {rec}")
        
        # Save full report
        with open('analysis_report.json', 'w') as f:
            json.dump(result, f, indent=2)
        print("\n Full report saved to: analysis_report.json")
        
    except Exception as e:
        print(f"\n Error: {str(e)}")


def example_2_optimize_summary():
    """Example 2: Optimize professional summary"""
    print("\n" + "=" * 70)
    print("EXAMPLE 2: Optimize Professional Summary")
    print("=" * 70)
    
    optimizer = CVOptimizer()
    
    # Critical keywords from analysis
    keywords = [
        "Python", "Flask", "FastAPI", "Docker", "Kubernetes",
        "microservices", "REST API", "CI/CD"
    ]
    
    current_summary = """
Tech & Engineering Professional with over 10 years of experience in backend development 
and procurement, renowned for pioneering innovative solutions and optimizing system efficiencies.
Masterfully skilled in Python, DevOps, and Dockerized microservices, fostering a collaborative 
and dynamic team environment.
"""
    
    try:
        result = optimizer.optimize_section(
            original_section=f"PROFESSIONAL SUMMARY\n\n{current_summary}",
            jd_text=SAMPLE_JD,
            keywords=keywords,
            optimization_focus="Target: Senior Backend Developer role, Emphasize: Python expertise, microservices, cloud, 2+ years specific backend experience"
        )
        
        print("\n ORIGINAL SUMMARY:")
        print(current_summary)
        
        print("\n OPTIMIZED SUMMARY:")
        print(result['optimized_content'])
        
        print("\n Key Changes Made:")
        print(result['changes_made'])
        
    except Exception as e:
        print(f"\n Error: {str(e)}")


def example_3_optimize_experience():
    """Example 3: Optimize experience section"""
    print("\n" + "=" * 70)
    print("EXAMPLE 3: Optimize Experience Bullets")
    print("=" * 70)
    
    optimizer = CVOptimizer()
    
    keywords = [
        "Python", "Flask", "FastAPI", "Docker", "microservices",
        "REST API", "PostgreSQL", "CI/CD", "GitHub Actions", "testing"
    ]
    
    original_bullets = """
PYTHON BACKEND DEVELOPER - Jan 2023 - Present
Freelance Remote

• Develop REST APIs with Flask, boosting backend efficiency and response times.
• Design Dockerized microservices for scalable deployments, enhancing system reliability.
• Create automated ETL pipelines, ensuring flawless data processing and deployment success.
• Conduct code reviews to optimize application stability and performance.
• Collaborate with frontend teams for seamless integration, improving project delivery timelines.
• Mentor junior developers, nurturing their skills and promoting a positive, collaborative team environment.
"""
    
    try:
        result = optimizer.optimize_section(
            original_section=original_bullets,
            jd_text=SAMPLE_JD,
            keywords=keywords,
            optimization_focus="Add specific metrics, emphasize testing, highlight CI/CD, quantify impact"
        )
        
        print("\n ORIGINAL BULLETS:")
        print(original_bullets)
        
        print("\n OPTIMIZED BULLETS:")
        print(result['optimized_content'])
        
        print("\n Keywords Incorporated:")
        print(result['keywords_used'])
        
    except Exception as e:
        print(f"\n Error: {str(e)}")


def example_4_generate_cover_letter():
    """Example 4: Generate cover letter"""
    print("\n" + "=" * 70)
    print("EXAMPLE 4: Generate Cover Letter")
    print("=" * 70)
    
    from app.services.cover_letter_gen import CoverLetterGenerator
    
    generator = CoverLetterGenerator()
    
    candidate_data = {
        'name': 'John Doe',
        'current_title': 'Python Backend Developer',
        'location': 'Amsterdam, Netherlands',
        'years_exp': '2+',
        'top_skills': [
            'Python (Flask, FastAPI)',
            'Docker & Kubernetes',
            'Microservices Architecture'
        ],
        'achievements': [
            'Designed automated ETL pipelines with 100% deployment success rate',
            'Built Dockerized microservices achieving 99.8% uptime',
            'Mentored 3 junior developers, improving team velocity by 25%'
        ]
    }
    
    job_data = {
        'company': 'TechCorp Netherlands',
        'position': 'Senior Backend Developer',
        'location': 'Amsterdam, Netherlands',
        'requirements': [
            'Python expertise with Flask/FastAPI',
            'Microservices architecture experience',
            'Docker and Kubernetes proficiency',
            'CI/CD pipeline implementation',
            'Mentoring junior developers'
        ]
    }
    
    try:
        result = generator.generate(candidate_data, job_data, tone="Professional")
        
        print("\n GENERATED COVER LETTER:")
        print(result['cover_letter'])
        
        print("\n Statistics:")
        print(f"  • Word count: {result['word_count']}")
        print(f"  • Keywords used: {len(result.get('keywords', []))}")
        
        # Save to file
        with open('cover_letter.txt', 'w') as f:
            f.write(result['cover_letter'])
        print("\n Cover letter saved to: cover_letter.txt")
        
    except Exception as e:
        print(f"\n Error: {str(e)}")


def example_5_full_workflow():
    """Example 5: Complete optimization workflow"""
    print("\n" + "=" * 70)
    print("EXAMPLE 5: Full Workflow (Analyze → Optimize → Cover Letter)")
    print("=" * 70)
    
    orchestrator = CVWorkflowOrchestrator()
    
    try:
        print("\n Starting full optimization workflow...")
        
        result = orchestrator.optimize_cv_for_job(
            cv_text=SAMPLE_CV,
            jd_text=SAMPLE_JD,
            generate_cover_letter=True
        )
        
        print("\n Workflow completed!")
        print(f"\n Final ATS Score: {result['ats_score']}/100")
        
        # Save all outputs
        with open('full_optimization_result.json', 'w') as f:
            json.dump(result, f, indent=2)
        
        print("\n Complete results saved to: full_optimization_result.json")
        
        print("\n" + "=" * 70)
        print("WORKFLOW SUMMARY")
        print("=" * 70)
        print("Analysis:  Completed")
        print("CV Optimization:  Completed")
        print("Cover Letter:  Completed")
        print(f"ATS Score: {result['ats_score']}/100")
        
    except Exception as e:
        print(f"\n Error: {str(e)}")


def example_6_batch_testing():
    """Example 6: Test against multiple job descriptions"""
    print("\n" + "=" * 70)
    print("EXAMPLE 6: Batch Testing (Multiple JDs)")
    print("=" * 70)
    
    analyzer = CVAnalyzer()
    
    # Multiple job descriptions for different roles
    job_descriptions = {
        'Backend Developer': SAMPLE_JD,
        
        'DevOps Engineer': """
        DevOps Engineer
        
        Requirements:
        - Strong experience with Docker, Kubernetes, Terraform
        - CI/CD pipeline implementation (Jenkins, GitHub Actions)
        - AWS or GCP cloud platforms
        - Python scripting for automation
        - Monitoring and observability (Prometheus, Grafana)
        - Linux system administration
        """,
        
        'Full Stack Developer': """
        Full Stack Developer
        
        Requirements:
        - Backend: Python (Flask/FastAPI) or Go
        - Frontend: React or Vue.js
        - REST API design and GraphQL
        - PostgreSQL database
        - Docker containerization
        - Agile/Scrum experience
        """,
        
        'Data Engineer': """
        Data Engineer
        
        Requirements:
        - Python for data processing
        - ETL pipeline development
        - SQL and database optimization
        - Apache Spark or similar big data tools
        - AWS data services (S3, Redshift, Lambda)
        - Data modeling and warehousing
        """
    }
    
    results = {}
    
    print("\n Analyzing CV against multiple roles...")
    
    for role, jd in job_descriptions.items():
        try:
            analysis = analyzer.analyze(SAMPLE_CV, jd)
            results[role] = {
                'ats_score': analysis['ats_score'],
                'matched_keywords': len(analysis['keyword_analysis']['matched_keywords']),
                'missing_keywords': len(analysis['keyword_analysis']['missing_critical'])
            }
            print(f"\n {role}: {analysis['ats_score']}/100")
            
        except Exception as e:
            print(f"\n {role}: Error - {str(e)}")
    
    # Show best matches
    print("\n" + "=" * 70)
    print("BEST ROLE MATCHES")
    print("=" * 70)
    
    sorted_results = sorted(results.items(), key=lambda x: x[1]['ats_score'], reverse=True)
    
    for i, (role, data) in enumerate(sorted_results, 1):
        print(f"\n{i}. {role}")
        print(f"   ATS Score: {data['ats_score']}/100")
        print(f"   Matched Keywords: {data['matched_keywords']}")
        print(f"   Missing Keywords: {data['missing_keywords']}")
    
    # Save comparison
    with open('role_comparison.json', 'w') as f:
        json.dump(results, f, indent=2)
    print("\n Comparison saved to: role_comparison.json")


# Main execution
if __name__ == "__main__":
    print("""

                    POWERCV EXAMPLE                                
          Optimizing CV for Backend Developer Roles                

""")
    
    # Choose which example to run
    import sys
    
    examples = {
        '1': ('Analyze CV', example_1_analyze_cv),
        '2': ('Optimize Summary', example_2_optimize_summary),
        '3': ('Optimize Experience', example_3_optimize_experience),
        '4': ('Generate Cover Letter', example_4_generate_cover_letter),
        '5': ('Full Workflow', example_5_full_workflow),
        '6': ('Batch Testing', example_6_batch_testing),
        'all': ('Run All Examples', None)
    }
    
    print("\nAvailable Examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    
    choice = input("\nSelect example (1-6 or 'all'): ").strip()
    
    if choice == 'all':
        for key, (name, func) in examples.items():
            if func:  # Skip 'all' option
                print(f"\n\n{'=' * 70}")
                print(f"Running: {name}")
                print(f"{'=' * 70}")
                func()
                input("\nPress Enter to continue to next example...")
    
    elif choice in examples and examples[choice][1]:
        examples[choice][1]()
    
    else:
        print(f"\n Invalid choice: {choice}")
        sys.exit(1)
    
    print("\n\n Examples completed!")
    print("\nNext steps:")
    print("  1. Review generated files (*.json, *.txt)")
    print("  2. Adjust prompts if needed (app/prompts/*.md)")
    print("  3. Integrate into your PowerCV application")
    print("  4. Test with real job descriptions")
